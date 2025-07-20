// 診療科カテゴリーに応じた診療科の読み込み
async function loadDepartmentsByCategory(category) {
    try {
        const response = await fetch(`/api/departments/by-category/${category}`);
        if (!response.ok) {
            throw new Error('Failed to load departments');
        }
        
        const data = await response.json();
        return data.departments;
    } catch (error) {
        console.error('Error loading departments:', error);
        return [];
    }
}

// 診療科選択肢のHTMLを動的に生成
function generateDepartmentOptionsHTML(departments) {
    let html = '';
    departments.forEach(dept => {
        html += `
            <label>
                <input type="radio" name="department" value="${dept.id}">
                <div class="department-icon" style="background-image: url('/images/${dept.icon}');"></div>
                ${dept.name_ja}
            </label>
        `;
    });
    return html;
}

// ページロード時に診療科を読み込んで表示
document.addEventListener('DOMContentLoaded', async function() {
    // URLから診療科カテゴリーを判定
    const path = window.location.pathname;
    let category = 'medical'; // デフォルト
    
    if (path.includes('/medical')) {
        category = 'medical';
    } else if (path.includes('/dental')) {
        category = 'dental';
    } else if (path.includes('/others')) {
        category = 'others';
    }
    
    // 診療科を読み込み
    const departments = await loadDepartmentsByCategory(category);
    
    // 診療科選択肢を更新
    const departmentOptionsContainer = document.querySelector('.department-options');
    if (departmentOptionsContainer && departments.length > 0) {
        departmentOptionsContainer.innerHTML = generateDepartmentOptionsHTML(departments);
    }
    
    // タイトルをカテゴリーに応じて更新
    const categoryNames = {
        'medical': '医科',
        'dental': '歯科',
        'others': 'その他'
    };
    
    const titleElement = document.querySelector('title');
    if (titleElement) {
        titleElement.textContent = `${categoryNames[category]} - ペルソナ自動生成AI`;
    }
});