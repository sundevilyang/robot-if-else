# robot-if-else
#### 启动数据库  mongodb 
[https://docs.mongodb.com/manual/installation/](https://docs.mongodb.com/manual/installation/)
#### 运行后台程序 robot-student-management

```
➜  robot-if-else git:(master) git clone https://github.com/Aym-fuhong/robot-student-management.git

Cloning into 'robot-student-management'...
remote: Counting objects: 250, done.
remote: Compressing objects: 100% (130/130), done.
remote: Total 250 (delta 155), reused 207 (delta 112), pack-reused 0
Receiving objects: 100% (250/250), 30.66 KiB | 0 bytes/s, done.
Resolving deltas: 100% (155/155), done.
Checking connectivity... done.

➜  robot-if-else git:(master) ✗ cd robot-student-management 
➜  robot-student-management git:(master) npm start

> mongoose01@1.0.0 start /home/zhyingjia/PythonProjects/robot-if-else/robot-student-management
> nodemon --exec npm run babel-node -- app.js

[nodemon] 1.11.0
[nodemon] to restart at any time, enter `rs`
[nodemon] watching: *.*
[nodemon] starting `npm run babel-node app.js`

> mongoose01@1.0.0 babel-node /home/zhyingjia/PythonProjects/robot-if-else/robot-student-management
> babel-node "app.js"

server started at http://localhost:3000
connect success

```
#### 运行微信程序 robot.py
 - 安装开发分支

```
pip3 install -U git+https://github.com/youfou/wxpy.git@develop
```

 - 运行程序

```
➜  robot-if-else git:(master) ✗ ./robot.py 

Getting uuid of QR code.
INFO:itchat:Getting uuid of QR code.
Downloading QR code.
INFO:itchat:Downloading QR code.
Please scan the QR code to log in.
INFO:itchat:Please scan the QR code to log in.

...微信二维码　（扫码登录）
```
