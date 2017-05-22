# robot-if-else
#### 安装Python3
[How To Install Python 3 and Set Up a Local Programming Environment on Ubuntu 16.04 | DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04)

```
sudo apt-get update
sudo apt-get -y upgrade
python3 -V
sudo apt-get install -y python3-pip

```

#### 安装和启动数据库  mongodb
[Install MongoDB Community Edition on Ubuntu — MongoDB Manual 3.4](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

`sudo service mongod start &>/dev/null &`

#### 安装Node
[Installing Node.js via package manager | Node.js](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions)

```
curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo apt-get install -y build-essential
```

#### 运行后台程序 robot-student-management

```
git clone https://github.com/sundevilyang/robot-student-management.git
cd robot-student-management
npm install
```
##### run nodejs in background
[PM2 - Advanced Node.js process manager](http://pm2.keymetrics.io/)

```
npm install pm2 -g
pm2 start app.js --watch
```

#### 运行微信程序 robot.py

```
git clone https://github.com/sundevilyang/robot-if-else.git
```

 ##### 安装开发分支

```
pip3 install -U git+https://github.com/youfou/wxpy.git@develop
```

 #### 运行程序

```
python3 robot.py
```

#### 微信二维码　（扫码登录）

#### 重启步骤
1. 打开一个terminal，输入`ssh root@172.104.71.9`
2. 启动mongodb `sudo service mongod start &>/dev/null &`
3. 运行node程序 `pm2 start app.js --watch`
4. 另外新开一个terminal，
  - 输入`ssh  root@172.104.71.9`;
  - 再输入`sudo tmux new -A -s wxpy -c /root/robot-if-else python3 robot.py`
