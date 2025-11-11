/**
 * 动画引擎 - 根据操作历史逐步演示数据结构变化
 */

export class AnimationEngine {
  constructor(options = {}) {
    this.operationHistory = []
    this.currentStepIndex = 0
    this.isPlaying = false
    this.speed = options.speed || 1000 // 每步延迟（毫秒）
    this.onStepCallback = options.onStep || (() => {})
    this.onCompleteCallback = options.onComplete || (() => {})
    this.timeoutId = null
  }

  /**
   * 设置操作历史
   */
  setOperationHistory(operationHistory) {
    this.operationHistory = operationHistory || []
    this.currentStepIndex = 0
    this.isPlaying = false
  }

  /**
   * 开始播放动画
   */
  play() {
    if (this.isPlaying) return
    if (this.currentStepIndex >= this.operationHistory.length) {
      this.currentStepIndex = 0 // 重新开始
    }

    this.isPlaying = true
    this._playNextStep()
  }

  /**
   * 暂停播放
   */
  pause() {
    this.isPlaying = false
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
    }
  }

  /**
   * 继续播放
   */
  resume() {
    if (!this.isPlaying) {
      this.play()
    }
  }

  /**
   * 停止并重置
   */
  stop() {
    this.pause()
    this.currentStepIndex = 0
  }

  /**
   * 跳到指定步骤
   */
  jumpToStep(stepIndex) {
    if (stepIndex >= 0 && stepIndex < this.operationHistory.length) {
      this.currentStepIndex = stepIndex
      this._notifyStep()
    }
  }

  /**
   * 下一步
   */
  nextStep() {
    if (this.currentStepIndex < this.operationHistory.length - 1) {
      this.currentStepIndex++
      this._notifyStep()
    }
  }

  /**
   * 上一步
   */
  previousStep() {
    if (this.currentStepIndex > 0) {
      this.currentStepIndex--
      this._notifyStep()
    }
  }

  /**
   * 获取当前步骤数据
   */
  getCurrentStep() {
    return this.operationHistory[this.currentStepIndex]
  }

  /**
   * 获取当前步骤索引
   */
  getCurrentStepIndex() {
    return this.currentStepIndex
  }

  /**
   * 获取总步骤数
   */
  getTotalSteps() {
    return this.operationHistory.length
  }

  /**
   * 设置动画速度
   */
  setSpeed(speed) {
    this.speed = speed
  }

  /**
   * 内部：播放下一步
   */
  _playNextStep() {
    if (!this.isPlaying) return

    if (this.currentStepIndex < this.operationHistory.length) {
      this._notifyStep()
      this.currentStepIndex++

      // 继续播放下一步
      this.timeoutId = setTimeout(() => {
        this._playNextStep()
      }, this.speed)
    } else {
      // 动画播放完成
      this.isPlaying = false
      this.currentStepIndex = this.operationHistory.length - 1
      this.onCompleteCallback()
    }
  }

  /**
   * 内部：通知当前步骤
   */
  _notifyStep() {
    const step = this.getCurrentStep()
    if (step) {
      this.onStepCallback({
        step,
        stepIndex: this.currentStepIndex,
        totalSteps: this.operationHistory.length
      })
    }
  }
}

/**
 * 树节点动画器 - 处理树结构的动画
 */
export class TreeAnimationHelper {
  /**
   * 根据操作步骤生成动画关键帧
   */
  static generateKeyframes(step) {
    const keyframes = {
      highlightedNodes: [],
      highlightedEdges: [],
      nodeAnimations: {},
      edgeAnimations: {}
    }

    if (!step) return keyframes

    // 根据操作类型设置高亮
    if (step.highlight_indices && Array.isArray(step.highlight_indices)) {
      keyframes.highlightedNodes = step.highlight_indices
    }

    // 设置指针位置
    if (step.pointers && typeof step.pointers === 'object') {
      for (const [pointerName, nodeId] of Object.entries(step.pointers)) {
        keyframes.highlightedNodes.push(nodeId)
      }
    }

    return keyframes
  }

  /**
   * 计算节点淡入淡出动画
   */
  static generateNodeFadeAnimation(nodeId, fadeIn = true) {
    return {
      nodeId,
      type: fadeIn ? 'fadeIn' : 'fadeOut',
      duration: 300,
      easing: 'ease-in-out'
    }
  }

  /**
   * 计算节点移动动画
   */
  static generateNodeMoveAnimation(nodeId, fromPos, toPos) {
    return {
      nodeId,
      type: 'move',
      fromPos,
      toPos,
      duration: 500,
      easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    }
  }

  /**
   * 生成脉冲动画（强调某个节点）
   */
  static generatePulseAnimation(nodeId) {
    return {
      nodeId,
      type: 'pulse',
      duration: 600,
      intensity: 1.2
    }
  }
}

/**
 * 线性结构动画器 - 处理数组/链表的动画
 */
export class LinearAnimationHelper {
  /**
   * 根据操作步骤生成动画关键帧
   */
  static generateKeyframes(step) {
    const keyframes = {
      highlightedIndices: [],
      pointerPositions: {},
      elementAnimations: []
    }

    if (!step) return keyframes

    // 高亮操作的元素
    if (step.highlight_indices && Array.isArray(step.highlight_indices)) {
      keyframes.highlightedIndices = step.highlight_indices
    }

    // 指针位置
    if (step.pointers && typeof step.pointers === 'object') {
      keyframes.pointerPositions = step.pointers
    }

    return keyframes
  }

  /**
   * 生成元素插入动画
   */
  static generateInsertAnimation(index) {
    return {
      type: 'insert',
      index,
      duration: 300,
      easing: 'ease-out'
    }
  }

  /**
   * 生成元素删除动画
   */
  static generateDeleteAnimation(index) {
    return {
      type: 'delete',
      index,
      duration: 300,
      easing: 'ease-in'
    }
  }

  /**
   * 生成元素交换动画
   */
  static generateSwapAnimation(index1, index2) {
    return {
      type: 'swap',
      index1,
      index2,
      duration: 400,
      easing: 'ease-in-out'
    }
  }

  /**
   * 生成移动动画
   */
  static generateMoveAnimation(fromIndex, toIndex) {
    return {
      type: 'move',
      fromIndex,
      toIndex,
      duration: 400,
      easing: 'ease-in-out'
    }
  }
}
