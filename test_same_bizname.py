#!/usr/bin/env python
"""
测试相同公众号的多篇文章导入
"""
import json
import requests
from datetime import datetime
import time

# 后端API地址
API_URL = 'http://localhost:8000'

# 先清空数据库
def clear_all_articles():
    print("正在清空所有文章...")
    
    response = requests.delete(f"{API_URL}/articles/all")
    
    if response.status_code == 200:
        print("成功清空所有文章")
    else:
        print(f"清空文章失败: {response.status_code}")
        print(response.text)

# 测试数据 - 同一公众号的3篇文章
test_data = {
    "data": [
        {
            "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=1&sn=a72a2e7c5adfd2157f513ca048d0c350",
            "title": "7248MWh，中国电气装备储能电芯集采",
            "digest": "储能行业大事件",
            "pub_time": "1749183018",
            "cover": "https://example.com/image1.jpg",
            "bizname": "储能之音",
            "biz": "MzI2Mjg2ODk4OA==",
            "mid": "2247515827",
            "idx": "1"
        },
        {
            "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=2&sn=eefa55c98023af1e63634358ae7118ca",
            "title": "鼓励用户侧储能参与需求响应，浙江2025迎峰度夏需求侧管理方案发布",
            "digest": "政策解读",
            "pub_time": "1749183018",
            "cover": "https://example.com/image2.jpg",
            "bizname": "储能之音",
            "biz": "MzI2Mjg2ODk4OA==",
            "mid": "2247515827",
            "idx": "2"
        },
        {
            "url": "http://mp.weixin.qq.com/s?__biz=MzI2Mjg2ODk4OA==&mid=2247515827&idx=3&sn=50c267518cd26a9b275409c72f1df399",
            "title": "400MW/1GWh用户侧储能项目落地四川广元",
            "digest": "项目新闻",
            "pub_time": "1749183018",
            "cover": "https://example.com/image3.jpg",
            "bizname": "储能之音",
            "biz": "MzI2Mjg2ODk4OA==", 
            "mid": "2247515827",
            "idx": "3"
        }
    ]
}

def test_import_articles():
    """测试导入多篇文章"""
    
    print("===== 导入同一公众号的多篇文章 =====")
    # 导入测试数据
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
        print("\n导入的文章详情:")
        for i, article in enumerate(articles):
            print(f"{i+1}. 标题: {article.get('title')}")
            print(f"   公众号: {article.get('bizname')}")
            print(f"   唯一ID: {article.get('unique_id')}")
            print(f"   发布时间: {article.get('pub_time_iso')}")
            print("")
    else:
        print(f"请求失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print(f"=== 开始测试相同公众号的多篇文章导入 {datetime.now().isoformat()} ===\n")
    
    # 清空所有文章
    clear_all_articles()
    
    time.sleep(1)  # 等待索引刷新
    
    # 测试导入
    test_import_articles()
    
    time.sleep(1)  # 等待索引刷新
    
    # 检查导入结果
    check_articles()
    
    print(f"\n=== 测试完成 {datetime.now().isoformat()} ===") 