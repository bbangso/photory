<template>
    <v-row no-gutters id="storysharelist" align="center" style="width: 100vw; height: 100vh;">
        <v-col>
            <div class="back">
                <img src="@/assets/loading/wave.png" style="max-width: -webkit-fill-available; position: absolute; bottom: 0;left: 0;">
            </div>
            <div class="tree">
                <img src="@/assets/asset/tree.png" style="max-width: -webkit-fill-available; position: absolute; bottom: 0;left: 0;">
            </div>
            <div class="word">
              <p style="font-family: 'UhBeeSeulvely'; font-size:60px; color:#3ba0a8;">ShareStory</p>
            </div>
            <div class="ani">
                <img src="@/assets/asset/rabbit.png" style="max-width:150px; position: absolute; bottom: 0;left: 0;">
            </div>
            <div class="ani2">
                <img @click="writeStory" src="@/assets/asset/owl_write.png" style="max-width:250px; position: absolute; bottom: 0;left: 0;">
            </div>
        </v-col>
        <v-col id="iconright" cols="3">
            <v-btn
                class="mx-2"
                fab
                color="#57bcc4"
                height="100"
                width="100"
                depressed
                @click="goFirstPage"
            >
                <v-icon
                    color="#c4e86b"
                    size=80
                >
                    mdi-arrow-collapse-left
                </v-icon>
            </v-btn>
            <v-btn
                class="mx-2"
                fab
                color="#57bcc4"
                small
                depressed
                height="100"
                width="100"
                @click="goPrePage"
            >
                <v-icon
                    color="#c4e86b"
                    size=80
                >
                    mdi-arrow-left
                </v-icon>
            </v-btn>
        </v-col>
        <v-col style="padding-left: 0px;padding-right: 0px;" cols="6">
            <div id="gallery_layout">
                <div class="gallery_content" v-for="( item ) in storyListData" v-bind:key="item.id" @click="()=>$router.push(`/sharestorypageboard/${item.id}`).catch(()=>{})">
                    <div id ="imgbox" style="float: left; position: relative;" >
                        <!-- 이미지 소스 바꿔놓기 bookcover가 null 일 때는 book.png -->
                        <div class="front"><img src="@/assets/book.png" alt="travel_img"></div>
                        <div id="back" style="position: absolute;  left: 50px;  top: 28px;  width: 55%; height: 63%;"><img src="@/assets/book_cover.png" alt="travel_img"></div>
                    </div>
                    <div class="content">
                            <h1>{{item.title}}</h1>
                            <p>{{item.writer}}</p>
                    </div>
                    <div class="overlay darkBlue" ></div>
                </div>
            </div>
        </v-col>
        <v-col id="iconleft" cols="3">
            <v-btn
                class="mx-2"
                fab
                color="#57bcc4"
                small
                depressed
                height="100"
                width="100"
                @click="goNextPage"
            >
                <v-icon
                    color="#c4e86b"
                    size =80
                >
                    mdi-arrow-right
                </v-icon>
            </v-btn>
            <v-btn
                class="mx-2"
                fab
                color="#57bcc4"
                small
                depressed
                height="100"
                width="100"
                @click="goLastpage"
            >
                <v-icon
                    color="#c4e86b"
                    size =80
                >
                    mdi-arrow-collapse-right
                </v-icon>
            </v-btn>
        </v-col>
        
    </v-row>
</template>

<script>
import axios from 'axios'
import router from '../router'
export default {
  data: () => ({
    num : 8,
    pagenum:0,
    storyListData:null,
    storyListCount :0,

  }),
  methods:{
      getList(){
        axios.get(`http://k3a205.p.ssafy.io:8000/board/list/${this.pagenum}/ `, { "Content-Type": "application-json" })
            .then(res => {
               this.storyListData = res.data
            })
            .catch((error) => {
                console.log(error.response.data);
            })
      },

      writeStory(){
          if(this.$store.state.isLogin){
              router.push('/sharestorywrite').catch(()=>{})
          }else{
              alert("로그인이 필요한 서비스 입니다.")
          }
      },
      goFirstPage(){
          this.pagenum =0;
          this.getList()
      },
      goPrePage(){
          if(this.pagenum<1){
              alert("첫 페이지입니다.")
          }else{
              this.pagenum = this.pagenum -1;
              this.getList()
          }
      },
      goLastpage(){
          let pagecount = Math.floor((this.storyListCount-1)/8);
          this.pagenum = pagecount;
          this.getList();
      },
      goNextPage(){
          let pagecount = Math.floor((this.storyListCount-1)/8);
          if(pagecount<=this.pagenum){
              alert("마지막 페이지입니다.")
          }else{
              this.pagenum = this.pagenum +1;
              this.getList()
          }
      }
  },
  created(){
    axios.get(`http://k3a205.p.ssafy.io:8000/board/list/${this.pagenum}/ `, { "Content-Type": "application-json" })
        .then(res => {
            this.storyListData = res.data
            console.log(res.data)
        })
        .catch((error) => {
            console.log(error.response.data);
        })
    
    axios.get(`http://k3a205.p.ssafy.io:8000/board/count/ `, { "Content-Type": "application-json" })
        .then(res => {
            this.storyListCount = res.data
            console.log(res.data)
        })
        .catch((error) => {
            console.log(error.response.data);
        })
      
  },
  
}
</script>

<style>

@import url(https://cdn.rawgit.com/openhiun/hangul/14c0f6faa2941116bb53001d6a7dcd5e82300c3f/nanumbarungothic.css); 

  body {
      font-family: "Nanum Barun Gothic", "Ubuntu Condensed", "Noto Sans Korean";;
  }

 #storysharelist{
    background-image:url("../assets/storysharehill.png");
	background-size : contain;
  }
  .gallery_content:hover .overlay.right {
      top: 0;
  }
  #gallery_layout {
      width: 800px;
      margin: 0 auto;
  }

  #gallery_layout:after {
      content: "";
      display: block;
      clear: both;
  }

  .gallery_content {
      position: relative;
      float: left;
      width: 25%;
      overflow: hidden;
  }

  .gallery_content img {
      width: 80%;
      height: 80%;
      display: block;
      margin: 0 auto;
      transition: all 1s ease-in-out;
  }
  .overlay.darkBlue {
      background-color:rgba(48, 97, 129, 0.6);
  }


  .content {
      z-index: 1;
      display: none;
      color: #fff;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
  }

  .content h1 {
      font-size: 1.2em;
      text-transform: uppercase;
      text-align: center;
  }
  .content p {
      padding: 2px 0;
      font-size: 0.8em;
      text-align: center;
  }        
  .gallery_content:hover .content {
      display: block;
      transition: all 1s ease-in-out;
  }

  .gallery_content:hover img {
      transform: scale(1.2);
      transition: all 1s ease-in-out;
  }

  .overlay {
      display: none;
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      transition: top 0.3s, right 0.3s, bottom 0.3s, left 0.3s;
  }

  .gallery_content:hover .overlay {
      display: block;
      transition: all 0.5s ease-in-out;
  }

  @media all and (min-width: 1000px) {
      /* #gallery_layout {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
      }   */
  }

  /* @media all and (max-width: 1800px) {
  #gallery_layout {
      width: 100%;
  }
  .gallery_content {
      width: 33%;
  }
  } */
  @media all and (max-width: 1000px) {
  #gallery_layout {
      width: 100%;
  }
  .gallery_content {
      width: 50%;
  }

  }
  @media all and (max-width: 499px) {
  #gallery_layout {
      width: 100%;
  }
  .gallery_content {
      width: 100%;
  }
 }
.tree{
    position: absolute;
    bottom: 0;
    left: 50vh;
    width:-webkit-fill-available;
}
.word{
    position: absolute;
    top: 10%;
    left: 0;
    width:-webkit-fill-available;
}
.ani{
    position: absolute;
    bottom: 0;
    left: 20%;
    width:-webkit-fill-available;
}
.ani2{
    position: absolute;
    bottom: 0;
    left:70%;
    width:-webkit-fill-available;
}
</style>
