import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import CategoryView from '../views/CategoryView.vue'
import LinearView from '../views/LinearView.vue'
import TreeView from '../views/TreeView.vue'
import LinearAlgorithm from '../views/LinearAlgorithm.vue'
import TreeNode from '../views/TreeNode.vue'
import TreeAlgorithm from '../views/TreeAlgorithm.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: WelcomeView,
      meta: { transitionName: 'fade' }
    },
    {
      path: '/category',
      name: 'category',
      component: CategoryView,
      meta: { transitionName: 'fade' }
    },
    {
      path: '/linear/:type?',
      name: 'linear',
      component: LinearView,
      meta: { transitionName: 'fade' }
    },
    {
      //线性结构可视化界面路由
      path: '/linear/:type',
      name: 'linearalgorithm',
      component: LinearAlgorithm,
      meta: { transitionName: 'fade' },
      props: true
    },
    {
      path: '/tree/:type?',
      name: 'tree',
      component: TreeView,
      meta: { transitionName: 'fade' }
    },
    {
      //树结构可视化界面路由
      path: '/tree/:type',
      name: 'treealgorithm',
      component: TreeAlgorithm,
      meta: { transitionName: 'fade' },
      props: true
    }
  ]
})

export default router
