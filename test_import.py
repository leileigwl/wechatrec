#!/usr/bin/env python
"""
测试文章数据导入脚本
用于测试多篇文章的数据导入功能
"""
import json
import requests
from datetime import datetime

# 后端API地址
API_URL = 'http://localhost:8000'

# 测试数据 - 包含多篇文章
test_data = {
    "data": {
        "timestamp": "2025-06-06 04:15:48",
        "method": "POST",
        "path": "/artlist/",
        "client": "116.196.91.130",
        "data": {
            "key": "AEqoeyurxc.98AEWQUcxi",
            "data": [
                {
                    "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=1&sn=a72a2e7c5adfd2157f513ca048d0c350&chksm=eb7417ba35a562b6dd423776435bf8eb0041320d101d680b292010cef857c6caff03219637d1&scene=0&xtrack=1#rd",
                    "title": "7248MWh，中国电气装备储能电芯集采",
                    "digest": "储能行业大事件",
                    "pub_time": "1749183018",
                    "cover": "https://mmbiz.qpic.cn/mmbiz_jpg/VjeqDTAdu7oSWJ5nQ2MqEfgqshLdZlByXVUSYCm8WibgxnrHcJVlpWHf8kUm3VXNRibc4Pg44DHLPtyAcah5cVwg/640?wxtype=jpeg&wxfrom=0",
                    "bizname": "储能之音",
                    "biz": "MzI2Mjg2ODk4OA=="
                },
                {
                    "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=2&sn=eefa55c98023af1e63634358ae7118ca&chksm=eb55567632b0be5f659498e1ec5ea67ab3f696e07cdd6615ccdeca46add32e0303e1f07d1fb0&scene=0&xtrack=1#rd",
                    "title": "鼓励用户侧储能参与需求响应，浙江2025迎峰度夏需求侧管理方案发布",
                    "digest": "政策解读",
                    "pub_time": "1749183018",
                    "cover": "https://mmbiz.qpic.cn/mmbiz_jpg/VjeqDTAdu7oSWJ5nQ2MqEfgqshLdZlByibb2CKib6o7uy25LUv003VXicicI70ia7Oj3mwopX6S7pEZQMViaQGM2e6cA/300?wxtype=jpeg&wxfrom=0",
                    "bizname": "储能之音",
                    "biz": "MzI2Mjg2ODk4OA=="
                },
                {
                    "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=3&sn=50c267518cd26a9b275409c72f1df399&chksm=ebcacbc3842b48d422bc06aaa603361f7ee925052bc3fd1a4ded3dde587dd5c61943dfd02640&scene=0&xtrack=1#rd",
                    "title": "400MW/1GWh用户侧储能项目落地四川广元",
                    "digest": "项目新闻",
                    "pub_time": "1749183018",
                    "cover": "https://mmbiz.qpic.cn/mmbiz_jpg/VjeqDTAdu7oSWJ5nQ2MqEfgqshLdZlByg0iceUzkHiblOSB3rTjmXCU06icGuibyK2s1lD3icLDwBhrLHObT4SW3oZQ/300?wxtype=jpeg&wxfrom=0",
                    "bizname": "储能之音",
                    "biz": "MzI2Mjg2ODk4OA=="
                }
            ],
            "stamp": 1749183348,
            "datatype": "article"
        },
        "_id": "68426b745f70b3a6765d9c2b"
    }
}

# 测试数据2 - 另一种格式（直接包含文章列表）
test_data2 = {
    "data": [
        {
            "url": "http://mp.weixin.qq.com/s?__biz=MzI5MTE2NDk4OA==&mid=2247515999&idx=1&sn=b72a2e7c5adfd2157f513ca048d0c350&chksm=eb7417ba35a562b6dd423776435bf8eb0041320d101d680b292010cef857c6caff03219637d1&scene=0&xtrack=1#rd",
            "title": "特斯拉发布全新家用储能产品Powerwall 3",
            "digest": "特斯拉发布会上的重磅产品",
            "pub_time": "1749183028",
            "cover": "https://example.com/image1.jpg",
            "bizname": "电动汽车资讯",
            "biz": "MzI5MTE2NDk4OA=="
        },
        {
            "url": "http://mp.weixin.qq.com/s?__biz=MzIxNTg2MT==&mid=2247515888&idx=1&sn=c72a2e7c5adfd2157f513ca048d0c350&chksm=eb7417ba35a562b6dd423776435bf8eb0041320d101d680b292010cef857c6caff03219637d1&scene=0&xtrack=1#rd",
            "title": "光伏发电技术最新进展：效率突破26%",
            "digest": "光伏技术重大突破",
            "pub_time": "1749183038",
            "cover": "https://example.com/image2.jpg",
            "bizname": "光伏产业观察",
            "biz": "MzIxNTg2MT=="
        }
    ]
}

def test_import_articles():
    """测试导入多篇文章"""
    
    print("===== 测试1: 导入多层嵌套数据 =====")
    # 导入测试数据1
    response = requests.post(
        f"{API_URL}/artlist/",
        json=test_data
    )
    
    # 检查响应
    if response.status_code == 200:
        result = response.json()
        print(f"成功导入: {result.get('saved', 0)} 篇文章")
        print(f"失败导入: {result.get('failed', 0)} 篇文章")
        print(f"消息: {result.get('message', '')}")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)
    
    print("\n===== 测试2: 导入直接数据 =====")
    # 导入测试数据2
    response = requests.post(
        f"{API_URL}/artlist/",
        json=test_data2
    )
    
    # 检查响应
    if response.status_code == 200:
        result = response.json()
        print(f"成功导入: {result.get('saved', 0)} 篇文章")
        print(f"失败导入: {result.get('failed', 0)} 篇文章")
        print(f"消息: {result.get('message', '')}")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)

def check_articles():
    """检查已导入的文章"""
    print("\n===== 检查导入的文章 =====")
    
    # 获取所有文章
    response = requests.get(f"{API_URL}/articles/?size=100")
    
    if response.status_code == 200:
        result = response.json()
        articles = result.get("articles", [])
        total = result.get("total", 0)
        
        print(f"总文章数: {total}")
        
        # 按公众号分组统计
        bizname_count = {}
        for article in articles:
            bizname = article.get("bizname", "未知公众号")
            if bizname in bizname_count:
                bizname_count[bizname] += 1
            else:
                bizname_count[bizname] = 1
        
        print("\n各公众号文章数:")
        for bizname, count in bizname_count.items():
            print(f"- {bizname}: {count}篇")
        
        # 显示部分文章标题
        print("\n最近导入的文章:")
        for i, article in enumerate(articles[:10]):
            print(f"{i+1}. {article.get('title')} ({article.get('bizname')}) - {article.get('pub_time_iso')}")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print(f"=== 开始测试文章导入 {datetime.now().isoformat()} ===\n")
    
    # 测试导入
    test_import_articles()
    
    # 检查导入结果
    check_articles()
    
    print(f"\n=== 测试完成 {datetime.now().isoformat()} ===") 