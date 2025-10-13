<template>
  <div class = "welcome-container":class="{'fade-out':fadeOut}">
    <h1 class="welcome-title">
      Welcome to DSVision!
    </h1>
  </div>
</template>

<script setup>
import { ref, onMounted} from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const fadeOut = ref(false)

onMounted(()=>{
  //1.5秒后淡出
  setTimeout(()=>{
    fadeOut.value = true
  },1500)

  //2.5秒跳转类别选择页面
  setTimeout(()=>{
    router.push('/category')
  },2500)
})
</script>

<style scoped>
.welcome-container{
  position:fixed;
  inset:0;
  background-color:white;
  display:flex;
  justify-content: center;
  align-items: center;
  align-content:center;
  transition:opacity 1s ease;
  opacity:1;
}
.welcome-container.fade-out {
  opacity: 0;
}
.welcome-title {
  font-family: Georgia,'Times New Roman',Times, serif;
  font-size: 4rem;
  font-weight: bold;
  color: black;
  text-align: center;
  padding: 0 2rem;
  animation: fadeIn 1s ease;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .welcome-title {
    font-size: 2rem;
  }
}

</style>
