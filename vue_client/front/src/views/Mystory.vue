<template>
  <div id="Mystory">
    <img id="bg" src="@/assets/hill.png" alt="" />
    <img
      src="@/assets/loading/wave.png"
      style="width: 100vw; position: fixed; bottom: 0; left: 0; height: 10%"
    />
    <div id="storyList">
      <h3 v-if="list0.length > 0">AI가 책을 만들고 있어요</h3>
      <div v-if="list0.length > 0" class="storyList">
        <img
          v-for="book in list0"
          :key="book.id"
          class="bookCover"
          :class="{ editable: !book.editable }"
          :src="`${url}/media/${book.images[0]}`"
          alt="작업중"
          @click="editFalse()"
        />
      </div>
      <h3>내 책 목록이에요</h3>
      <div class="storyList">
        <!-- {{list1}} -->
        <img
          v-for="book in list1"
          :key="book.id"
          class="bookCover"
          :class="{ editable: !book.editable }"
          :src="`${url}/media/${book.images[0]}`"
          :alt="book.title"
          @click="editStory(book.id)"
        />
        <img
          v-if="list1.length === 0"
          class="bookCover"
          alt="빈 공간"
          src="@/assets/asset/book.png"
        />
        <h1 v-if="list1.length === 0">새 책을 추가해 보세요</h1>
      </div>
      <h3>내 책 목록이에요. 공유해서 확인해보세요</h3>
      <div class="storyList">
        <img
          v-for="book in list2"
          :key="book.id"
          class="bookCover"
          :src="`${url}${book.content0}`"
          :alt="book.title"
          @click="lookbook(book.id)"
        />
        <img
          v-if="list2.length === 0"
          class="bookCover"
          alt="빈 공간"
          src="@/assets/asset/book.png"
        />
        <h1 v-if="list2.length === 0">책을 완성해 보세요</h1>
      </div>
    </div>
  </div>
</template>
<script>
import axios from "axios";
const url = "http://k3a205.p.ssafy.io:8000";

export default {
  // 사진이름 url/stpk_photonum_styleNum.jpg
  // story_pk/
  name: "Mystory",
  data() {
    return {
      list: [],
      list0: [],
      list1: [],
      list2: [],
      update: 0,
      url: url,
    };
  },
  created() {
    if (!this.$store.state.isLogin) {
      alert("로그인이 필요합니다");
      this.$router.push('/');
    }
    const config = {
      headers: {
        Authorization: "JWT " + this.$store.state.token,
        "Content-Type": "application-json",
      },
    };
    axios.get(url + "/storys/", config).then((res) => {
      this.list = res.data;
      this.list.forEach((item) => {
        item.images.sort();
      });
      this.list0 = this.list.filter((item) => !item.editable);
      this.list1 = this.list.filter((item) => item.editable && !item.complete);
    });
    axios.get(url + "/storys/books/", config).then((res) => {
      this.list2 = res.data;
    });
    this.update = setInterval(() => {
      axios.get(url + "/storys/",config).then((res) => {
        this.list = res.data;
        this.list.forEach((item) => {
          item.images.sort();
        });
      });
    }, 5000);
  },
  mounted() {
    this.$nextTick(() => {
      this.addTitle();
    });
  },
  beforeUpdate() {
    this.$nextTick(() => {
      this.addTitle();
    });
  },
  beforeDestroy(){
    clearInterval(this.update)
  },
  methods: {
    editStory(id) {
      this.$router.push("EditStory/" + id);
    },
    editFalse() {
      alert("서버 작업이 완료되면 만들기 시작할 수 있어요");
    },
    addTitle() {
      document.querySelectorAll(".labelT").forEach((item) => item.remove());
      document.querySelectorAll(".bookCover").forEach((item) => {
        let T = document.createElement("span");
        T.className = "labelT";
        T.innerText = item.alt;
        T.style.position = "absolute";
        T.style.left = `${item.offsetLeft}px`;
        T.style.top = `${item.offsetTop + item.clientHeight}px`;
        T.style.width = `${item.clientWidth}px`;
        T.style.backgroundColor = "rgba($color: #eee, $alpha: 0.5)";
        item.parentNode.appendChild(T);
      });
    },
    lookbook(id){
      this.$router.push('/sharestorypagemystory/'+id)
    }
  },
};
</script>
<style lang="scss" scoped>
#Mystory {
  position: relative;
  height: 100%;
  overflow: hidden;
  width: 100vw;
  #bg {
    position: fixed;
    left: 0;
    top: 50px;
    width: 100vw;
    height: 100vh;
  }
  #storyList {
    max-height: 100vh;
    overflow-y: auto;
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    padding-top: 50px;
  }
  .storyList {
    padding: 15px;
    // width: 100vw;
    border: 1px #aaa solid;
    margin: 10px;
    display: flex;
    flex-flow: row wrap;
    justify-content: flex-start;
    align-content: flex-start;
    .bookCover {
      height: 20vmin;
      width: 15vmin;
      min-height: 140px;
      min-width: 105px;
      margin: 0 10px 20px 10px;
      &:hover {
        cursor: pointer;
      }
    }
  }
}
</style>