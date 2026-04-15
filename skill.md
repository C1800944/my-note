---
name: js-basics-practice
description: 本 skill 用于创建 JavaScript 基础练习页面，包含变量定义、变量类型、表达式、流程控制和函数等核心知识点。
---

# JavaScript 基础练习

## 练习目标

本页面用于练习 JavaScript 基础知识，包括以下内容：

1. **变量定义** - 使用 var、let、const 声明变量
2. **变量类型** - string、number、boolean、array、object、null、undefined
3. **表达式** - 算术表达式、逻辑表达式
4. **流程控制** - if/else 条件语句、for 循环
5. **函数** - 函数定义与调用

## 完整代码示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript 基础练习</title>
</head>
<body>
    <h1>JavaScript 基础练习</h1>
    
    <h2>1. 变量定义</h2>
    <script>
        var name = "张三";      // var 声明
        let age = 25;           // let 声明
        const PI = 3.14159;     // const 声明常量
        
        console.log("姓名:", name);
        console.log("年龄:", age);
        console.log("圆周率:", PI);
    </script>
    
    <h2>2. 数据类型</h2>
    <script>
        let str = "Hello";      // 字符串
        let num = 100;          // 数字
        let bool = true;        // 布尔值
        let arr = [1, 2, 3];    // 数组
        let obj = {a: 1, b: 2}; // 对象
        
        console.log(typeof str);   // string
        console.log(typeof num);   // number
        console.log(typeof bool);  // boolean
        console.log(typeof arr);   // object
        console.log(typeof obj);   // object
    </script>
    
    <h2>3. 表达式</h2>
    <script>
        let a = 10, b = 3;
        console.log("加法:", a + b);        // 13
        console.log("减法:", a - b);        // 7
        console.log("乘法:", a * b);        // 30
        console.log("除法:", a / b);        // 3.33
        console.log("取余:", a % b);        // 1
        
        let isAdult = age >= 18;  // 逻辑表达式
        console.log("是否成年:", isAdult);
    </script>
    
    <h2>4. 流程控制</h2>
    <script>
        // if/else
        if (age >= 18) {
            console.log("已成年");
        } else {
            console.log("未成年");
        }
        
        // for 循环
        for (let i = 0; i < 5; i++) {
            console.log("循环第", i + 1, "次");
        }
    </script>
    
    <h2>5. 函数</h2>
    <script>
        function add(a, b) {
            return a + b;
        }
        
        let result = add(5, 3);
        console.log("5 + 3 =", result);
    </script>
</body>
</html>
```

## 使用方法

1. 将上述代码保存为 `.html` 文件
2. 用浏览器打开查看
3. 按 F12 打开控制台查看输出结果
4. 根据需要修改代码进行练习

## 注意事项

- `var`、`let`、`const` 的区别需要理解
- `const` 声明的常量不能重新赋值
- `typeof` 可以用来查看变量类型
- 条件语句和循环语句是流程控制的基础
- 函数可以封装可复用的代码逻辑
