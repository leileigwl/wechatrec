#!/usr/bin/env python3
"""
测试脚本，用于向API发送示例数据
"""
import json
import requests
from datetime import datetime

# API地址
API_URL = "http://localhost:8000"

# 示例文章数据
sample_data = {
    "data":{
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
          "digest": "",
          "pub_time": "1749183018",
          "cover": "https://mmbiz.qpic.cn/mmbiz_jpg/VjeqDTAdu7oSWJ5nQ2MqEfgqshLdZlByXVUSYCm8WibgxnrHcJVlpWHf8kUm3VXNRibc4Pg44DHLPtyAcah5cVwg/640?wxtype=jpeg&wxfrom=0",
          "bizname": "储能之音",
          "biz": "MzI2Mjg2ODk4OA=="
        },
        {
          "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=2&sn=eefa55c98023af1e63634358ae7118ca&chksm=eb55567632b0be5f659498e1ec5ea67ab3f696e07cdd6615ccdeca46add32e0303e1f07d1fb0&scene=0&xtrack=1#rd",
          "title": "鼓励用户侧储能参与需求响应，浙江2025迎峰度夏需求侧管理方案发布",
          "digest": "",
          "pub_time": "1749183018",
          "cover": "https://mmbiz.qpic.cn/mmbiz_jpg/VjeqDTAdu7oSWJ5nQ2MqEfgqshLdZlByibb2CKib6o7uy25LUv003VXicicI70ia7Oj3mwopX6S7pEZQMViaQGM2e6cA/300?wxtype=jpeg&wxfrom=0",
          "bizname": "储能之音",
          "biz": "MzI2Mjg2ODk4OA=="
        },
        {
          "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=3&sn=50c267518cd26a9b275409c72f1df399&chksm=ebcacbc3842b48d422bc06aaa603361f7ee925052bc3fd1a4ded3dde587dd5c61943dfd02640&scene=0&xtrack=1#rd",
          "title": "400MW/1GWh用户侧储能项目落地四川广元",
          "digest": "",
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

def test_save_articles():
    """测试保存文章接口"""
    print("测试保存文章接口...")
    
    url = f"{API_URL}/artlist/"
    response = requests.post(url, json=sample_data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.status_code == 200

def test_search_articles():
    """测试搜索文章接口"""
    print("\n测试搜索文章接口...")
    
    # 测试几个不同的搜索关键词
    keywords = ["储能", "电网", "光伏", "特斯拉", "氢能"]
    
    for keyword in keywords:
        url = f"{API_URL}/search/?q={keyword}&page=1&size=10"
        response = requests.get(url)
        
        print(f"\n关键词 '{keyword}':")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"找到 {data.get('total', 0)} 条结果，用时 {data.get('took', 0)/1000:.3f} 秒")
            
            # 显示前2条结果的标题
            results = data.get("results", [])
            for i, result in enumerate(results[:2]):
                print(f"  {i+1}. {result.get('title', '无标题')}")
            
            if len(results) > 2:
                print(f"  ... 还有 {len(results)-2} 条结果")
        else:
            print(f"响应内容: {response.text}")

def test_logs():
    """测试获取日志接口"""
    print("\n测试获取日志接口...")
    
    url = f"{API_URL}/logs/?page=1&size=5"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"找到 {data.get('total', 0)} 条日志")
        
        # 显示前2条日志
        logs = data.get("logs", [])
        for i, log in enumerate(logs[:2]):
            print(f"  {i+1}. {log.get('timestamp')} - {log.get('method')} {log.get('path')}")
        
        if len(logs) > 2:
            print(f"  ... 还有 {len(logs)-2} 条日志")
    else:
        print(f"响应内容: {response.text}")

def main():
    """主函数"""
    print("开始测试WeChat文章搜索系统API...\n")
    
    # 测试保存文章
    save_success = test_save_articles()
    
    if save_success:
        # 如果保存成功，等待1秒让Elasticsearch索引数据
        import time
        print("\n等待Elasticsearch索引数据...")
        time.sleep(1)
        
        # 测试搜索文章
        test_search_articles()
        
        # 测试获取日志
        test_logs()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 