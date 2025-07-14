// 全局变量
const API_URL = 'http://localhost:8000'; // 后端API地址，根据实际部署修改
let currentQuery = ''; // 当前搜索查询
let currentPage = 1; // 当前页码
const PAGE_SIZE = 10; // 每页结果数量
let allBiznames = new Set(); // 存储所有公众号名称
let selectedBizname = ''; // 当前选中的公众号
let allResults = []; // 存储所有搜索结果

// DOM元素
document.addEventListener('DOMContentLoaded', () => {
    const homeSearch = document.getElementById('home-search');
    const resultsSearch = document.getElementById('results-search');
    const searchResults = document.getElementById('search-results');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsSearchInput = document.getElementById('results-search-input');
    const resultsSearchButton = document.getElementById('results-search-button');
    const resultStats = document.getElementById('result-stats');
    const resultItems = document.getElementById('result-items');
    const pagination = document.getElementById('pagination');
    const loader = document.getElementById('loader');
    const biznameFilter = document.getElementById('bizname-filter');
    const biznameList = document.getElementById('bizname-list');

    // 事件监听器
    // 主页搜索按钮
    searchButton.addEventListener('click', () => {
        performSearch(searchInput.value);
    });

    // 主页搜索输入框回车键
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch(searchInput.value);
        }
    });

    // 结果页搜索按钮
    resultsSearchButton.addEventListener('click', () => {
        performSearch(resultsSearchInput.value);
    });

    // 结果页搜索输入框回车键
    resultsSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch(resultsSearchInput.value);
        }
    });

    // 返回主页（点击标题）
    document.querySelector('.results-logo h2').addEventListener('click', () => {
        goToHomePage();
    });

    // 检查URL参数，如果有查询参数，则执行搜索
    const urlParams = new URLSearchParams(window.location.search);
    const queryParam = urlParams.get('q');
    const pageParam = urlParams.get('page');
    const biznameParam = urlParams.get('bizname');
    
    if (queryParam) {
        currentQuery = queryParam;
        currentPage = pageParam ? parseInt(pageParam) : 1;
        selectedBizname = biznameParam || '';
        searchInput.value = currentQuery;
        resultsSearchInput.value = currentQuery;
        executeSearch(currentQuery, currentPage);
    }

    /**
     * 执行搜索操作
     * @param {string} query - 搜索关键词
     */
    function performSearch(query) {
        if (!query || query.trim().length < 2) {
            alert('请输入至少2个字符的搜索关键词');
            return;
        }

        currentQuery = query.trim();
        currentPage = 1;
        selectedBizname = ''; // 重置选中的公众号
        
        // 更新URL
        updateURLParameters(currentQuery, currentPage, selectedBizname);
        
        // 执行搜索
        executeSearch(currentQuery, currentPage);
    }

    /**
     * 更新URL参数，不刷新页面
     * @param {string} query - 搜索关键词
     * @param {number} page - 页码
     * @param {string} bizname - 公众号名称
     */
    function updateURLParameters(query, page, bizname = '') {
        const url = new URL(window.location);
        url.searchParams.set('q', query);
        url.searchParams.set('page', page);
        
        if (bizname) {
            url.searchParams.set('bizname', bizname);
        } else {
            url.searchParams.delete('bizname');
        }
        
        window.history.pushState({}, '', url);
    }

    /**
     * 执行API搜索
     * @param {string} query - 搜索关键词
     * @param {number} page - 页码
     */
    function executeSearch(query, page) {
        // 显示加载动画
        showLoader();
        
        // 隐藏主页搜索，显示结果页搜索
        homeSearch.style.display = 'none';
        resultsSearch.style.display = 'block';

        // 构建API URL
        const apiUrl = `${API_URL}/search/?q=${encodeURIComponent(query)}&page=${page}&size=${PAGE_SIZE}`;
        console.log('搜索URL:', apiUrl);

        // 发起API请求
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('搜索请求失败');
                }
                return response.json();
            })
            .then(data => {
                console.log('搜索结果:', data);
                // 存储所有结果
                allResults = data.results || [];
                console.log('处理后的结果数组:', allResults);
                
                // 收集所有公众号名称
                allBiznames = new Set();
                allResults.forEach(article => {
                    if (article.bizname) {
                        allBiznames.add(article.bizname);
                    }
                });
                console.log('公众号列表:', Array.from(allBiznames));
                
                // 显示公众号筛选
                updateBiznameFilter();
                
                // 显示搜索结果
                displaySearchResults(data, query);
                
                // 隐藏加载动画
                hideLoader();
            })
            .catch(error => {
                console.error('搜索错误:', error);
                // 显示错误信息
                displayError('搜索请求失败，请稍后重试');
                // 隐藏加载动画
                hideLoader();
            });
    }

    /**
     * 更新公众号筛选列表
     */
    function updateBiznameFilter() {
        // 清空列表
        biznameList.innerHTML = '';
        
        if (allBiznames.size === 0) {
            biznameFilter.style.display = 'none';
            return;
        }
        
        // 添加"全部"选项
        const allOption = document.createElement('div');
        allOption.className = `bizname-item ${selectedBizname === '' ? 'active' : ''}`;
        allOption.textContent = '全部公众号';
        allOption.addEventListener('click', () => {
            filterByBizname('');
        });
        biznameList.appendChild(allOption);
        
        // 添加各公众号选项
        Array.from(allBiznames).sort().forEach(bizname => {
            const biznameItem = document.createElement('div');
            biznameItem.className = `bizname-item ${selectedBizname === bizname ? 'active' : ''}`;
            biznameItem.textContent = bizname;
            biznameItem.addEventListener('click', () => {
                filterByBizname(bizname);
            });
            biznameList.appendChild(biznameItem);
        });
        
        // 显示筛选区域
        biznameFilter.style.display = 'block';
    }

    /**
     * 按公众号筛选结果
     * @param {string} bizname - 公众号名称
     */
    function filterByBizname(bizname) {
        selectedBizname = bizname;
        currentPage = 1;
        
        // 更新URL
        updateURLParameters(currentQuery, currentPage, selectedBizname);
        
        // 筛选并显示结果
        const filteredResults = selectedBizname 
            ? allResults.filter(article => article.bizname === selectedBizname)
            : allResults;
        
        // 更新激活状态
        document.querySelectorAll('.bizname-item').forEach(item => {
            if ((item.textContent === '全部公众号' && selectedBizname === '') || 
                (item.textContent === selectedBizname)) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // 显示筛选后的结果
        displayFilteredResults(filteredResults);
    }

    /**
     * HTML字符反转义（将&lt;转换回<等）
     * @param {string} escapedHtml - 已转义的HTML字符串
     * @returns {string} 反转义后的HTML字符串
     */
    function unescapeHTML(escapedHtml) {
        if (!escapedHtml) return '';
        
        // 创建一个临时元素
        const doc = new DOMParser().parseFromString(escapedHtml, 'text/html');
        // 获取解析后的文本
        return doc.documentElement.textContent;
    }

    /**
     * 处理包含<em>标签的文本，确保正确高亮显示
     * @param {string} text - 可能包含<em>标签的文本
     * @returns {string} 处理后的HTML
     */
    function processHighlightedText(text) {
        if (!text) return '';
        
        // 检查是否包含未渲染的HTML标签
        if (typeof text === 'string' && (text.includes('&lt;em&gt;') || text.includes('&lt;/em&gt;'))) {
            // 替换转义的HTML标签
            text = text.replace(/&lt;em&gt;/g, '<em>').replace(/&lt;\/em&gt;/g, '</em>');
            console.log('已替换转义的标签:', text);
        }
        
        // 如果文本中包含<em>标签的文本表示
        if (typeof text === 'string' && text.includes('<em>') && text.includes('</em>')) {
            console.log('已包含em标签，直接返回:', text);
            return text;
        }
        
        console.log('无标签，返回普通文本:', text);
        // 纯文本，不需要高亮
        return text;
    }

    /**
     * 显示筛选后的结果
     * @param {Array} filteredResults - 筛选后的结果数组
     */
    function displayFilteredResults(filteredResults) {
        // 清空结果区域
        resultItems.innerHTML = '';
        
        // 显示结果统计
        const totalFiltered = filteredResults.length;
        resultStats.textContent = `找到约 ${totalFiltered} 条${selectedBizname ? '来自 "' + selectedBizname + '" 的' : ''}结果`;
        
        // 显示结果区域
        searchResults.style.display = 'block';

        if (totalFiltered === 0) {
            resultItems.innerHTML = '<div class="no-results">没有找到符合条件的文章</div>';
            pagination.innerHTML = '';
            return;
        }

        // 获取结果模板
        const resultTemplate = document.getElementById('result-item-template');
        
        // 遍历结果并显示
        filteredResults.forEach(article => {
            const resultItem = document.importNode(resultTemplate.content, true);
            
            // 设置标题和链接
            const titleLink = resultItem.querySelector('.result-title a');
            titleLink.innerHTML = processHighlightedText(article.title) || '无标题';
            titleLink.href = article.url || '#';
            
            // 设置摘要
            const snippet = resultItem.querySelector('.result-snippet');
            snippet.innerHTML = processHighlightedText(article.digest) || '无摘要';
            
            // 设置公众号名称
            const bizname = resultItem.querySelector('.bizname');
            bizname.textContent = article.bizname || '未知公众号';
            
            // 设置发布日期
            const pubDate = resultItem.querySelector('.pub-date');
            if (article.pub_time_iso) {
                const date = new Date(article.pub_time_iso);
                pubDate.textContent = formatDate(date);
            } else {
                pubDate.textContent = '未知日期';
            }
            
            // 添加到结果区域
            resultItems.appendChild(resultItem);
        });
        
        // 不需要创建分页，因为我们显示所有筛选后的结果
        pagination.innerHTML = '';
    }

    /**
     * 显示搜索结果
     * @param {Object} data - 搜索结果数据
     * @param {string} query - 搜索关键词
     */
    function displaySearchResults(data, query) {
        console.log('开始渲染搜索结果:', data);
        
        // 应用公众号筛选
        const filteredResults = selectedBizname 
            ? data.results.filter(article => article.bizname === selectedBizname)
            : data.results;
            
        console.log('过滤后的结果:', filteredResults);
        
        // 清空结果区域
        resultItems.innerHTML = '';
        
        // 显示结果统计
        const totalResults = filteredResults.length;
        const originalTotal = data.total || 0;
        
        resultStats.textContent = selectedBizname
            ? `找到约 ${totalResults} 条来自 "${selectedBizname}" 的结果（总共 ${originalTotal} 条，用时${data.took ? (data.took/1000).toFixed(2) : '0.00'}秒）`
            : `找到约 ${originalTotal} 条结果（用时${data.took ? (data.took/1000).toFixed(2) : '0.00'}秒）`;
        
        // 显示结果区域
        searchResults.style.display = 'block';

        if (filteredResults.length === 0) {
            resultItems.innerHTML = selectedBizname
                ? `<div class="no-results">没有找到与 "${escapeHTML(query)}" 相关的来自 "${escapeHTML(selectedBizname)}" 的文章</div>`
                : `<div class="no-results">没有找到与 "${escapeHTML(query)}" 相关的文章</div>`;
            pagination.innerHTML = '';
            return;
        }

        // 获取结果模板
        const resultTemplate = document.getElementById('result-item-template');
        
        console.log('开始渲染结果项，数量:', filteredResults.length);
        
        // 遍历结果并显示
        filteredResults.forEach((article, index) => {
            console.log(`渲染结果项 ${index+1}:`, article);
            const resultItem = document.importNode(resultTemplate.content, true);
            
            // 设置标题和链接
            const titleLink = resultItem.querySelector('.result-title a');
            titleLink.innerHTML = processHighlightedText(article.title) || '无标题';
            titleLink.href = article.url || '#';
            
            // 设置摘要
            const snippet = resultItem.querySelector('.result-snippet');
            snippet.innerHTML = processHighlightedText(article.digest) || '无摘要';
            
            // 设置公众号名称
            const bizname = resultItem.querySelector('.bizname');
            bizname.textContent = article.bizname || '未知公众号';
            
            // 设置发布日期
            const pubDate = resultItem.querySelector('.pub-date');
            if (article.pub_time_iso) {
                const date = new Date(article.pub_time_iso);
                pubDate.textContent = formatDate(date);
            } else {
                pubDate.textContent = '未知日期';
            }
            
            // 添加到结果区域
            resultItems.appendChild(resultItem);
        });
        
        console.log('渲染完成，准备创建分页');
        
        // 创建分页控件
        createPagination(data.total, currentPage, PAGE_SIZE);
    }

    /**
     * 创建分页导航
     * @param {number} total - 总结果数
     * @param {number} currentPage - 当前页码
     * @param {number} pageSize - 每页结果数
     */
    function createPagination(total, currentPage, pageSize) {
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
     * 跳转到指定页码
     * @param {number} page - 页码
     */
    function goToPage(page) {
        if (page === currentPage) return;
        
        currentPage = page;
        
        // 更新URL参数
        updateURLParameters(currentQuery, currentPage, selectedBizname);
        
        // 执行搜索
        executeSearch(currentQuery, currentPage);
        
        // 滚动到顶部
        window.scrollTo(0, 0);
    }

    /**
     * 返回主页
     */
    function goToHomePage() {
        currentQuery = '';
        currentPage = 1;
        selectedBizname = '';
        allBiznames = new Set();
        allResults = [];
        
        searchInput.value = '';
        resultsSearchInput.value = '';
        
        // 显示主页搜索，隐藏结果页搜索和结果
        homeSearch.style.display = 'flex';
        resultsSearch.style.display = 'none';
        searchResults.style.display = 'none';
        biznameFilter.style.display = 'none';
        
        // 清除URL参数
        window.history.pushState({}, '', window.location.pathname);
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
     * 显示加载动画
     */
    function showLoader() {
        loader.style.display = 'flex';
    }

    /**
     * 隐藏加载动画
     */
    function hideLoader() {
        loader.style.display = 'none';
    }

    /**
     * 显示错误信息
     * @param {string} message - 错误信息
     */
    function displayError(message) {
        searchResults.style.display = 'block';
        resultStats.textContent = '';
        resultItems.innerHTML = `<div class="error-message">${escapeHTML(message)}</div>`;
        pagination.innerHTML = '';
    }

    /**
     * 转义HTML字符
     * @param {string} unsafe - 不安全的字符串
     * @returns {string} 转义后的字符串
     */
    function escapeHTML(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}); 