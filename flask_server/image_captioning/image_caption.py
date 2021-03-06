import pickle
import tensorflow as tf
import numpy as np

class BahdanauAttention(tf.keras.Model):
    def __init__(self, units):
        super(BahdanauAttention, self).__init__()
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, features, hidden):
        # features(CNN_encoder output) shape == (batch_size, 64, embedding_dim)

        # hidden shape == (batch_size, hidden_size)
        # hidden_with_time_axis shape == (batch_size, 1, hidden_size)
        hidden_with_time_axis = tf.expand_dims(hidden, 1)

        # attention_hidden_layer shape == (batch_size, 64, units)
        attention_hidden_layer = (tf.nn.tanh(self.W1(features) +
                                            self.W2(hidden_with_time_axis)))

        # score shape == (batch_size, 64, 1)
        # This gives you an unnormalized score for each image feature.
        score = self.V(attention_hidden_layer)

        # attention_weights shape == (batch_size, 64, 1)
        attention_weights = tf.nn.softmax(score, axis=1)

        # context_vector shape after sum == (batch_size, hidden_size)
        context_vector = attention_weights * features
        context_vector = tf.reduce_sum(context_vector, axis=1)

        return context_vector, attention_weights


class CNN_Encoder(tf.keras.Model):
    # Since you have already extracted the features and dumped it using pickle
    # This encoder passes those features through a Fully connected layer
    def __init__(self, embedding_dim):
        super(CNN_Encoder, self).__init__()
        # shape after fc == (batch_size, 64, embedding_dim)
        self.fc = tf.keras.layers.Dense(embedding_dim)

    def call(self, x):
        x = self.fc(x)
        x = tf.nn.relu(x)
        return x
    
    
class RNN_Decoder(tf.keras.Model):
    def __init__(self, embedding_dim, units, vocab_size):
        super(RNN_Decoder, self).__init__()
        self.units = units

        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(self.units,
                                    return_sequences=True,
                                    return_state=True,
                                    recurrent_initializer='glorot_uniform')
        self.fc1 = tf.keras.layers.Dense(self.units)
        self.fc2 = tf.keras.layers.Dense(vocab_size)

        self.attention = BahdanauAttention(self.units)

    def call(self, x, features, hidden):
        # defining attention as a separate model
        context_vector, attention_weights = self.attention(features, hidden)

        # x shape after passing through embedding == (batch_size, 1, embedding_dim)
        x = self.embedding(x)

        # x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
        x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
        
        # passing the concatenated vector to the GRU
        output, state = self.gru(x)

        # shape == ()
        x = self.fc1(output)

        # x shape == (batch_size * max_length, hidden_size)
        x = tf.reshape(x, (-1, x.shape[2]))

        # output shape == (batch_size * max_length, vocab)
        x = self.fc2(x)

        return x, state, attention_weights

    def reset_state(self, batch_size):
        return tf.zeros((batch_size, self.units))


class Image_caption():
    def __init__(self):

        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                # Currently, memory growth needs to be the same across GPUs
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                # Memory growth must be set before GPUs have been initialized
                print(e)



        with open('image_captioning/checkpoints/train3/train_captions.pickle','rb') as fr:
            self.train_captions = pickle.load(fr)
        
        self.max_length = 616435
        self.top_k = 30000
        self.embedding_dim = 512
        self.units = 512
        self.vocab_size = self.top_k + 1
        self.features_shape = 2048
        self.attention_features_shape = 64

        self.encoder = CNN_Encoder(self.embedding_dim)
        self.decoder = RNN_Decoder(self.embedding_dim, self.units, self.vocab_size)
        self.optimizer = tf.keras.optimizers.Adam()
        
        self.checkpoint_path = './image_captioning/checkpoints/train3'
        self.ckpt = tf.train.Checkpoint(encoder=self.encoder,
                                        decoder=self.decoder,
                                        optimzier=self.optimizer)
        self.ckpt_manager = tf.train.CheckpointManager(self.ckpt, self.checkpoint_path, max_to_keep=5)

        start_epoch = 0
        if self.ckpt_manager.latest_checkpoint:
            start_epoch = int(self.ckpt_manager.latest_checkpoint.split('-')[-1])
            
            self.ckpt.restore(self.ckpt_manager.latest_checkpoint)

            print(start_epoch, "epoch start")
        self.image_model = tf.keras.applications.InceptionV3(
            include_top = False,
            weights='imagenet'
        )
        

        self.new_input = self.image_model.input
        self.hidden_layer = self.image_model.layers[-1].output

        self.image_features_extract_model = tf.keras.Model(self.new_input, self.hidden_layer)

        self.tokenizer = tf.keras.preprocessing.text.Tokenizer(
            num_words= self.top_k,
            oov_token="<unk>",
            filters='!"#$%&()*+.,-/:;=?@[\]^_`{|}~ '
        )

        self.tokenizer.fit_on_texts(self.train_captions)
        self.tokenizer.word_index['<pad>'] = 0
        self.tokenizer.index_word[0] = '<pad>'

    def evaluate(self, image):
        attention_plot = np.zeros((self.max_length, self.attention_features_shape))
        hidden = self.decoder.reset_state(batch_size=1)    
        temp_input = tf.expand_dims(self.load_image(image)[0], 0)
        img_tensor_val = self.image_features_extract_model(temp_input)
        img_tensor_val = tf.reshape(img_tensor_val, (img_tensor_val.shape[0], -1, img_tensor_val.shape[3]))

        features = self.encoder(img_tensor_val)
        dec_input = tf.expand_dims([self.tokenizer.word_index['<start>']],0)
        result = []

        for i in range(self.max_length):
            predictions, hidden, attention_weights = self.decoder(dec_input, features, hidden)
            attention_plot[i] = tf.reshape(attention_weights, (-1,)).numpy()
            predicted_id = tf.random.categorical(predictions, 1)[0][0].numpy()

            if self.tokenizer.index_word[predicted_id] == '<end>':
                return result, attention_plot
            result.append(self.tokenizer.index_word[predicted_id])
            dec_input = tf.expand_dims([predicted_id],0)
        
        attention_plot = attention_plot[:len(result), :]
        return result, attention_plot


    def load_image(self, image_path):
        img = tf.io.read_file(image_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, (299, 299))
        img = tf.keras.applications.inception_v3.preprocess_input(img)
        return img, image_path