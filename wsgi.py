# -*- coding: utf-8 -*-
import datetime

from flask import Flask, render_template

from pyecharts import Pie, Line, Bar, Grid, Page

from sam.OnlineUsers import getOnlineUserCount

from api.api_mod import api_bp
from history.history_mod import history_bp
from today.today_mod import today_bp

from network.cisco_ap_grabber import mac_grabber, name_grabber

from dao.dao import getPyodbcDao, getMysqlDao

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(history_bp, url_prefix='/history')
app.register_blueprint(today_bp, url_prefix='/today')


@app.route('/building')
def building_list():
    return render_template('building.html')


@app.route('/vl/<data>')
def vlan_list(data):
    return render_template('vl.html', qdata=data)


@app.route('/subnet/<data>')
def subnet(data):
    return render_template('subnet.html', qdata=data)


def mypie():
    # 生成饼图
    attr = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
    v1 = [11, 12, 13, 10, 10, 10]
    pie = Pie("饼图示例")
    pie.add("", attr, v1, is_label_show=True)
    return pie


@app.route('/')
def realtime():
    opt = [
        {"key": 'OccupyBandwidth', 'ylabel': 'Mbps', 'gtitle': '今日带宽使用', 'label': False},
        {"key": 'OnlineUsers', 'ylabel': '人', 'gtitle': '今日在线人数', 'label': False},
        # {"key": 'SendAndReceiceMails', 'ylabel': '封', 'gtitle': '今日收发邮件'},
        {"key": 'PortalAccess', 'ylabel': '次', 'gtitle': '今日门户访问', 'label': False},
        # {"key": 'EcardUse', 'ylabel': '次', 'gtitle': '今日一卡通使用'}
    ]
    ouc = getOnlineUserCount()
    page = Page()
    for item in opt:
        itemValue, dateList = getPyodbcDao().today_graph_data(item['key'])
        lfig = Line()
        lfig.add(item['gtitle'], dateList, itemValue, is_label_show=item['label'])
        page.add(lfig)
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    myechart = page.render_embed()  # 饼图
    host = REMOTE_HOST  # js文件源地址
    script_list = page.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("index.html", myechart=myechart, host=host, script_list=script_list, onlineusers=ouc)


@app.route('/day7')
def day7():
    opt = [
        {"key": 'OccupyBandwidth', 'ylabel': 'Mbps', 'gtitle': '最近7日带宽使用', 'label': True},
        {"key": 'OnlineUsers', 'ylabel': '人', 'gtitle': '最近7日在线人数', 'label': True},
        {"key": 'SendAndReceiceMails', 'ylabel': '封', 'gtitle': '最近7日收发邮件', 'label': True},
        {"key": 'PortalAccess', 'ylabel': '次', 'gtitle': '最近7日门户访问', 'label': True},
        {"key": 'EcardUse', 'ylabel': '次', 'gtitle': '最近7日一卡通使用', 'label': True}
    ]
    page = Page()
    for item in opt:
        itemValue, dateList = getPyodbcDao().query_graph_data(item['key'])
        lfig = Bar()
        lfig.add(item['gtitle'], dateList, itemValue, is_label_show=item['label'])
        page.add(lfig)
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    myechart = page.render_embed()  # 饼图
    host = REMOTE_HOST  # js文件源地址
    script_list = page.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("day7.html", myechart=myechart, host=host, script_list=script_list)


@app.route("/pie")
def tp():
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    pie = mypie()
    myechart = pie.render_embed()  # 饼图
    host = REMOTE_HOST  # js文件源地址
    script_list = pie.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("pie.html", myechart=myechart, host=host, script_list=script_list)


@app.route("/lf")
def line():
    v, d = getPyodbcDao().query_graph_data("OnlineUsers")
    lfig = Line()
    lfig.add("", d, v, is_label_show=True)
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    myechart = lfig.render_embed()  # 饼图
    host = REMOTE_HOST  # js文件源地址
    script_list = lfig.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("user-statistics.html", myechart=myechart, host=host, script_list=script_list)


@app.route("/t")
def bwuse():
    data = getMysqlDao().get_today_bwuse()
    label = data[0]
    attr = data[14]
    page = Page()
    for i in range(1, 14):
        lfig = Line()
        lfig.add(label[i - 1], attr, data[i], is_label_show=False)
        page.add(lfig)
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    myechart = page.render_embed()  # 饼图
    host = REMOTE_HOST  # js文件源地址
    script_list = page.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("bandwidth.html", myechart=myechart, host=host, script_list=script_list)


@app.route("/wsp")
def wsp():
    attr, data = getMysqlDao().get_website_speed()
    page = Page()
    for key, val in data.items():
        lfig = Line()
        lfig.add(key, attr, val, is_label_show=False)
        page.add(lfig)
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    myechart = page.render_embed()
    host = REMOTE_HOST  # js文件源地址
    script_list = page.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("site-speed.html", myechart=myechart, host=host, script_list=script_list)


@app.route("/mg")
def mg():
    attr, data = getMysqlDao().query_max_value()
    page = Page()
    for key, val in data.items():
        lfig = Bar()
        lfig.add(key, attr, val, is_label_show=True)
        page.add(lfig)
    REMOTE_HOST = "https://pyecharts.github.io/assets/js"
    myechart = page.render_embed()  # 饼图
    host = REMOTE_HOST  # js文件源地址
    script_list = page.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_template("month.html", myechart=myechart, host=host, script_list=script_list)


@app.route("/aplist")
def aplist():
    ap_name_list = name_grabber()
    offline_ap = getMysqlDao().query_offline_ap_by_name(ap_name_list)
    return render_template('cisco.html', offline_ap=offline_ap, online=len(ap_name_list))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
