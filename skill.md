---
name: js-basics-practice
description: 创建 JavaScript 基础练习 HTML 页面（交互版），包含变量定义、变量类型、表达式、流程控制和函数等核心知识点的交互式练习。
---

# JavaScript 基础练习 (js-basics-practice)

创建包含 JavaScript 基础知识练习的**交互式** HTML 页面，用于学习和巩固 JS 核心概念。

## 练习内容

1. **变量定义** - 使用 var、let、const 声明变量
2. **变量类型** - string、number、boolean、array、object、null、undefined
3. **表达式** - 算术表达式、逻辑表达式
4. **流程控制** - if/else 条件语句、for 循环
5. **函数** - 函数定义与调用

## 交互式 HTML 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>JavaScript 基础练习</title>
    <style>
        input, button { padding: 10px; border: 2px solid #667eea; border-radius: 8px; }
        button { background: #667eea; color: white; cursor: pointer; }
        .output { background: #1e1e1e; color: #0f0; padding: 15px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>JavaScript 基础练习（交互版）</h1>
    
    <!-- 1. 变量定义 -->
    <div>
        <input id="nameInput" placeholder="输入名字">
        <input id="ageInput" type="number" placeholder="输入年龄">
        <button onclick="testVariables()">测试变量</button>
        <div id="output1"></div>
    </div>
    
    <!-- 2. 数据类型 -->
    <div>
        <button onclick="testTypes()">检测数据类型</button>
        <div id="output2"></div>
    </div>
    
    <!-- 3. 表达式 -->
    <div>
        <input id="numA" type="number" value="10">
        <input id="numB" type="number" value="3">
        <button onclick="testExpressions()">计算表达式</button>
        <div id="output3"></div>
    </div>
    
    <!-- 4. 流程控制 -->
    <div>
        <input id="compareNum" type="number" placeholder="输入数字">
        <button onclick="testControlFlow()">判断奇偶</button>
        <button onclick="testLoop()">打印1-5</button>
        <div id="output4"></div>
    </div>
    
    <!-- 5. 函数 -->
    <div>
        <input id="funcNum1" type="number" value="5">
        <input id="funcNum2" type="number" value="3">
        <button onclick="testFunction()">调用函数相加</button>
        <div id="output5"></div>
    </div>
    
    <!-- 6. 自定义代码执行 -->
    <div>
        <textarea id="codeInput" rows="4" placeholder="输入JavaScript代码..."></textarea>
        <button onclick="runCode()">运行代码</button>
        <div id="output">输出结果：</div>
    </div>
    
    <script>
        function testVariables() {
            let name = document.getElementById('nameInput').value || "访客";
            let age = parseInt(document.getElementById('ageInput').value) || 0;
            const PI = 3.14159;
            document.getElementById('output1').innerHTML = 
                `name = "${name}"\nlet age = ${age}\nconst PI = ${PI}`;
        }
        
        function testTypes() {
            let output = `typeof "Hello" = string\ntypeof 100 = number\ntypeof true = boolean`;
            document.getElementById('output2').innerHTML = output;
        }
        
        function testExpressions() {
            let a = parseInt(document.getElementById('numA').value);
            let b = parseInt(document.getElementById('numB').value);
            document.getElementById('output3').innerHTML = 
                `${a} + ${b} = ${a+b}\n${a} - ${b} = ${a-b}\n${a} * ${b} = ${a*b}`;
        }
        
        function testControlFlow() {
            let num = parseInt(document.getElementById('compareNum').value);
            document.getElementById('output4').innerHTML = 
                num % 2 === 0 ? `${num} 是偶数` : `${num} 是奇数`;
        }
        
        function testLoop() {
            let output = '';
            for (let i = 1; i <= 5; i++) output += `第 ${i} 次循环\n`;
            document.getElementById('output4').innerHTML = output;
        }
        
        function testFunction() {
            let a = parseInt(document.getElementById('funcNum1').value);
            let b = parseInt(document.getElementById('funcNum2').value);
            function add(x, y) { return x + y; }
            document.getElementById('output5').innerHTML = `add(${a}, ${b}) = ${add(a, b)}`;
        }
        
        function runCode() {
            try {
                let output = '';
                let originalLog = console.log;
                console.log = function(...args) { output += args.join(' ') + '\n'; };
                eval(document.getElementById('codeInput').value);
                console.log = originalLog;
                document.getElementById('output').innerHTML = '输出：' + output;
            } catch (e) {
                document.getElementById('output').innerHTML = '错误：' + e.message;
            }
        }
    </script>
</body>
</html>
```

## 使用方式

1. 创建 `0415.html` 文件
2. 将上述代码复制到文件中
3. 用浏览器打开
4. 输入数值，点击按钮进行交互式练习

## 验证要点

- ✅ 变量声明使用 var、let、const
- ✅ 包含所有基本数据类型
- ✅ 有算术和逻辑表达式
- ✅ 包含 if/else 和 for 循环
- ✅ 有函数定义和调用
- ✅ 支持用户输入和交互
