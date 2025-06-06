// 全局变量
const API_URL = 'http://localhost:8000'; // 后端API地址，根据实际部署修改
let currentPage = 1; // 当前页码
const PAGE_SIZE = 20; // 每页结果数量
let totalArticles = 0; // 文章总数

// DOM元素
document.addEventListener('DOMContentLoaded', () => {
    const articlesList = document.getElementById('articles-list');
    const pagination = document.getElementById('pagination');
    const loader = document.getElementById('loader');
    const sortBySelect = document.getElementById('sort-by');
    const sortOrderSelect = document.getElementById('sort-order');
    const applyFilterButton = document.getElementById('apply-filter');
    
    // 初始加载文章
    loadArticles(currentPage);
    
    // 事件监听器
    if (applyFilterButton) {
        applyFilterButton.addEventListener('click', () => {
            currentPage = 1;
            loadArticles(currentPage);
        });
    }
    
    /**
     * 加载文章列表
     * @param {number} page - 页码
     */
    function loadArticles(page) {
        // 显示加载动画
        if (loader) loader.style.display = 'flex';
        
        // 获取排序选项
        const sortBy = sortBySelect ? sortBySelect.value : 'pub_time_iso';
        const sortOrder = sortOrderSelect ? sortOrderSelect.value : 'desc';
        
        // 构建API URL
        const apiUrl = `${API_URL}/articles/?page=${page}&size=${PAGE_SIZE}&sort_by=${sortBy}&sort_order=${sortOrder}`;
        
        // 发起API请求
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取文章列表失败');
                }
                return response.json();
            })
            .then(data => {
                // 存储总数
                totalArticles = data.total || 0;
                
                // 显示文章列表
                displayArticles(data.articles || []);
                
                // 创建分页
                createPagination(data.total, currentPage, PAGE_SIZE);
                
                // 更新统计信息
                updateStats(data.total, currentPage, PAGE_SIZE);
                
                // 隐藏加载动画
                if (loader) loader.style.display = 'none';
            })
            .catch(error => {
                console.error('获取文章列表错误:', error);
                
                // 显示错误信息
                if (articlesList) {
                    articlesList.innerHTML = `<div class="error-message">获取文章列表失败: ${error.message}</div>`;
                }
                
                // 隐藏加载动画
                if (loader) loader.style.display = 'none';
            });
    }
    
    /**
     * 显示文章列表
     * @param {Array} articles - 文章数组
     */
    function displayArticles(articles) {
        if (!articlesList) return;
        
        // 清空列表
        articlesList.innerHTML = '';
        
        if (articles.length === 0) {
            articlesList.innerHTML = '<div class="no-articles">没有找到文章</div>';
            return;
        }
        
        // 创建表格
        const table = document.createElement('table');
        table.className = 'articles-table';
        
        // 创建表头
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>ID</th>
                <th>标题</th>
                <th>公众号</th>
                <th>发布日期</th>
                <th>操作</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // 创建表体
        const tbody = document.createElement('tbody');
        
        // 遍历文章
        articles.forEach(article => {
            const tr = document.createElement('tr');
            
            // 格式化日期
            const pubDate = article.pub_time_iso 
                ? formatDate(new Date(article.pub_time_iso))
                : '未知日期';
            
            // 设置行内容
            tr.innerHTML = `
                <td title="${article.unique_id}">${truncateText(article.unique_id, 10)}</td>
                <td><a href="${article.url}" target="_blank" title="${article.title}">${truncateText(article.title, 40)}</a></td>
                <td>${article.bizname || '未知公众号'}</td>
                <td>${pubDate}</td>
                <td>
                    <button class="view-btn" data-id="${article.unique_id}">查看</button>
                    <button class="delete-btn" data-id="${article.unique_id}">删除</button>
                </td>
            `;
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        articlesList.appendChild(table);
        
        // 添加删除按钮事件
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const articleId = e.target.getAttribute('data-id');
                if (confirm('确定要删除这篇文章吗？此操作不可撤销！')) {
                    deleteArticle(articleId);
                }
            });
        });
        
        // 添加查看按钮事件
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const articleId = e.target.getAttribute('data-id');
                viewArticleDetails(articleId, articles);
            });
        });
    }
    
    /**
     * 查看文章详情
     * @param {string} articleId - 文章ID
     * @param {Array} articles - 文章数组
     */
    function viewArticleDetails(articleId, articles) {
        // 查找文章
        const article = articles.find(a => a.unique_id === articleId);
        if (!article) return;
        
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'modal';
        
        // 设置模态框内容
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal">&times;</span>
                <h2>${article.title || '无标题'}</h2>
                <p><strong>公众号:</strong> ${article.bizname || '未知公众号'}</p>
                <p><strong>发布日期:</strong> ${article.pub_time_iso ? formatDate(new Date(article.pub_time_iso)) : '未知日期'}</p>
                <p><strong>文章ID:</strong> ${article.unique_id}</p>
                <div class="article-digest">
                    <strong>摘要:</strong>
                    <p>${article.digest || '无摘要'}</p>
                </div>
                <div class="article-actions">
                    <a href="${article.url}" target="_blank" class="action-btn">打开原文</a>
                    <button class="action-btn delete-action" data-id="${article.unique_id}">删除文章</button>
                </div>
            </div>
        `;
        
        // 添加到文档
        document.body.appendChild(modal);
        
        // 显示模态框
        setTimeout(() => {
            modal.style.display = 'flex';
        }, 10);
        
        // 关闭模态框事件
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        });
        
        // 删除按钮事件
        modal.querySelector('.delete-action').addEventListener('click', () => {
            if (confirm('确定要删除这篇文章吗？此操作不可撤销！')) {
                deleteArticle(articleId);
                modal.style.opacity = '0';
                setTimeout(() => {
                    document.body.removeChild(modal);
                }, 300);
            }
        });
    }
    
    /**
     * 删除文章
     * @param {string} articleId - 文章ID
     */
    function deleteArticle(articleId) {
        // 显示加载动画
        if (loader) loader.style.display = 'flex';
        
        // 构建API URL
        const apiUrl = `${API_URL}/article/${articleId}`;
        
        // 发起删除请求
        fetch(apiUrl, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('删除文章失败');
            }
            return response.json();
        })
        .then(data => {
            // 显示成功消息
            alert(data.message || '文章删除成功');
            
            // 重新加载文章列表
            loadArticles(currentPage);
        })
        .catch(error => {
            console.error('删除文章错误:', error);
            alert('删除文章失败: ' + error.message);
            
            // 隐藏加载动画
            if (loader) loader.style.display = 'none';
        });
    }
    
    /**
     * 创建分页导航
     * @param {number} total - 总结果数
     * @param {number} currentPage - 当前页码
     * @param {number} pageSize - 每页结果数
     */
    function createPagination(total, currentPage, pageSize) {
        if (!pagination) return;
        
        pagination.innerHTML = '';
        
        const totalPages = Math.ceil(total / pageSize);
        if (totalPages <= 1) return;
        
        // 创建上一页按钮
        const prevArrow = document.createElement('div');
        prevArrow.className = `page-arrow ${currentPage === 1 ? 'disabled' : ''}`;
        prevArrow.innerHTML = '<span class="material-icons">arrow_back</span>';
        if (currentPage > 1) {
            prevArrow.addEventListener('click', () => goToPage(currentPage - 1));
        }
        pagination.appendChild(prevArrow);
        
        // 确定显示的页码范围
        let startPage = Math.max(1, currentPage - 4);
        let endPage = Math.min(totalPages, startPage + 9);
        
        // 调整起始页，确保最多显示10个页码
        if (endPage - startPage < 9) {
            startPage = Math.max(1, endPage - 9);
        }
        
        // 创建页码按钮
        for (let i = startPage; i <= endPage; i++) {
            const pageNumber = document.createElement('div');
            pageNumber.className = `page-number ${i === currentPage ? 'active' : ''}`;
            pageNumber.textContent = i;
            pageNumber.addEventListener('click', () => goToPage(i));
            pagination.appendChild(pageNumber);
        }
        
        // 创建下一页按钮
        const nextArrow = document.createElement('div');
        nextArrow.className = `page-arrow ${currentPage === totalPages ? 'disabled' : ''}`;
        nextArrow.innerHTML = '<span class="material-icons">arrow_forward</span>';
        if (currentPage < totalPages) {
            nextArrow.addEventListener('click', () => goToPage(currentPage + 1));
        }
        pagination.appendChild(nextArrow);
    }
    
    /**
     * 更新统计信息
     * @param {number} total - 总结果数
     * @param {number} currentPage - 当前页码
     * @param {number} pageSize - 每页结果数
     */
    function updateStats(total, currentPage, pageSize) {
        const statsElem = document.getElementById('articles-stats');
        if (!statsElem) return;
        
        const start = (currentPage - 1) * pageSize + 1;
        const end = Math.min(currentPage * pageSize, total);
        
        if (total === 0) {
            statsElem.textContent = '没有文章';
        } else {
            statsElem.textContent = `显示 ${start}-${end}，共 ${total} 篇文章`;
        }
    }
    
    /**
     * 跳转到指定页码
     * @param {number} page - 页码
     */
    function goToPage(page) {
        if (page === currentPage) return;
        
        currentPage = page;
        loadArticles(currentPage);
        
        // 滚动到顶部
        window.scrollTo(0, 0);
    }
    
    /**
     * 格式化日期
     * @param {Date} date - 日期对象
     * @returns {string} 格式化后的日期字符串
     */
    function formatDate(date) {
        if (!(date instanceof Date) || isNaN(date)) {
            return '未知日期';
        }
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    }
    
    /**
     * 截断文本
     * @param {string} text - 文本
     * @param {number} maxLength - 最大长度
     * @returns {string} 截断后的文本
     */
    function truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}); 