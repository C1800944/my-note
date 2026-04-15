---
name: js-basics-practice
description: 创建 JavaScript 基础练习 HTML 页面，包含变量定义、变量类型、表达式、流程控制和函数等核心知识点的练习。
---

# JavaScript 基础练习 (js-basics-practice)

创建包含 JavaScript 基础知识练习的 HTML 页面，用于学习和巩固 JS 核心概念。

## 练习内容

1. **变量定义** - 使用 var、let、const 声明变量
2. **变量类型** - string、number、boolean、array、object、null、undefined
3. **表达式** - 算术表达式、逻辑表达式
4. **流程控制** - if/else 条件语句、for 循环
5. **函数** - 函数定义与调用

## HTML 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>JavaScript 基础练习</title>
</head>
<body>
    <h1>JavaScript 基础练习</h1>
    
    <!-- 1. 变量定义 -->
    <h2>1. 变量定义</h2>
    <script>
        var name = "张三";
        let age = 25;
        const PI = 3.14159;
        console.log(name, age, PI);
    </script>
    
    <!-- 2. 数据类型 -->
    <h2>2. 数据类型</h2>
    <script>
        let str = "Hello";
        let num = 100;
        let bool = true;
        let arr = [1, 2, 3];
        let obj = {name: "张三", age: 25};
        console.log(typeof str, typeof num, typeof bool);
    </script>
    
    <!-- 3. 表达式 -->
    <h2>3. 表达式</h2>
    <script>
        let sum = 10 + 5;
        let isAdult = age >= 18;
        console.log("sum:", sum, "isAdult:", isAdult);
    </script>
    
    <!-- 4. 流程控制 -->
    <h2>4. 流程控制</h2>
    <script>
        if (age >= 18) {
            console.log("已成年");
        } else {
            console.log("未成年");
        }
        
        for (let i = 0; i < 5; i++) {
            console.log("第" + i + "次循环");
        }
    </script>
    
    <!-- 5. 函数 -->
    <h2>5. 函数</h2>
    <script>
        function greet(name) {
            return "你好, " + name;
        }
        console.log(greet("张三"));
    </script>
</body>
</html>
```

## 使用方式

1. 创建 `0415.html` 文件
2. 将上述代码复制到文件中
3. 用浏览器打开查看效果
4. 按 F12 打开控制台查看输出

## 验证要点

- 变量声明使用 var、let、const
- 包含所有基本数据类型
- 有算术和逻辑表达式
- 包含 if/else 和 for 循环
- 有函数定义和调用
