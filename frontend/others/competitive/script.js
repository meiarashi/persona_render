// 競合分析機能のJavaScript

// グローバル変数
let googleMapsLoaded = false;
let mapInstance = null;
let markers = [];
let infoWindow = null;

// Google Maps APIを動的に読み込む
async function loadGoogleMapsAPI() {
    if (googleMapsLoaded) return;
    
    try {
        const response = await fetch('/api/google-maps-key');
        if (!response.ok) throw new Error('Failed to get API key');
        
        const data = await response.json();
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${data.api_key}&callback=onGoogleMapsLoaded&language=ja&region=JP`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    } catch (error) {
        console.error('Failed to load Google Maps:', error);
    }
}

// Google Maps API読み込み完了時のコールバック
window.onGoogleMapsLoaded = function() {
    googleMapsLoaded = true;
    console.log('Google Maps API loaded');
};

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('competitive-analysis-form');
    const analyzingScreen = document.getElementById('analyzing-screen');
    const resultScreen = document.getElementById('result-screen');
    
    // 全診療科リスト（管理者用）
    const medicalDepartments = [
        // 医科
        '内科', '外科', '小児科', '皮膚科', '整形外科',
        '眼科', '耳鼻咽喉科', '泌尿器科', '産婦人科', '放射線科',
        '麻酔科', '救急科', '形成外科', '脳神経外科', '心療内科', '呼吸器内科',
        // 歯科
        '一般歯科', '小児歯科', '矯正歯科', '審美歯科',
        // その他
        '精神科', '美容外科', 'リハビリテーション科', '皮膚科（美容）',
        'ペインクリニック', '漢方内科', '在宅診療', '健診・人間ドック'
    ];
    
    // 初期化
    init();
    
    function init() {
        // 診療科チェックボックスを生成
        renderDepartmentCheckboxes();
        
        // イベントリスナーの設定
        setupEventListeners();
        
        // 郵便番号検索機能
        setupPostalCodeSearch();
    }
    
    function renderDepartmentCheckboxes() {
        const container = document.querySelector('.department-checkbox-grid');
        container.innerHTML = '';
        
        medicalDepartments.forEach(dept => {
            const div = document.createElement('div');
            div.className = 'department-checkbox';
            div.innerHTML = `
                <input type="checkbox" id="dept-${dept}" name="departments" value="${dept}">
                <label for="dept-${dept}">${dept}</label>
            `;
            container.appendChild(div);
        });
    }
    
    function setupEventListeners() {
        // 次へボタン
        document.querySelectorAll('.next-step-btn').forEach(btn => {
            btn.addEventListener('click', handleNextStep);
        });
        
        // 前へボタン
        document.querySelectorAll('.prev-step-btn').forEach(btn => {
            btn.addEventListener('click', handlePrevStep);
        });
        
        // 分析開始ボタン
        document.querySelector('.analyze-btn').addEventListener('click', handleAnalyze);
    }
    
    function handleNextStep(e) {
        const currentStep = parseInt(e.target.closest('.form-step').dataset.step);
        
        // バリデーション
        if (!validateStep(currentStep)) {
            return;
        }
        
        // 次のステップへ
        showStep(currentStep + 1);
    }
    
    function handlePrevStep(e) {
        const currentStep = parseInt(e.target.closest('.form-step').dataset.step);
        showStep(currentStep - 1);
    }
    
    function showStep(stepNumber) {
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });
        
        const targetStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
        }
    }
    
    function validateStep(stepNumber) {
        switch(stepNumber) {
            case 1:
                // クリニック情報の検証
                const clinicName = document.getElementById('clinic-name').value.trim();
                const address = document.getElementById('address').value.trim();
                const checkedDepts = document.querySelectorAll('input[name="departments"]:checked');
                
                if (!clinicName) {
                    showModal('クリニック名を入力してください。');
                    return false;
                }
                
                if (!address) {
                    showModal('住所を入力してください。');
                    return false;
                }
                
                if (checkedDepts.length === 0) {
                    showModal('診療科を少なくとも1つ選択してください。');
                    return false;
                }
                
                return true;
                
            case 2:
                // 分析範囲は必ず選択されているので追加検証不要
                return true;
                
            case 3:
                // 任意項目なので検証不要
                return true;
                
            default:
                return true;
        }
    }
    
    function setupPostalCodeSearch() {
        const postalSearchBtn = document.querySelector('.postal-search-btn');
        const postalCodeInput = document.getElementById('postal-code');
        const addressInput = document.getElementById('address');
        
        postalSearchBtn.addEventListener('click', async function() {
            const postalCode = postalCodeInput.value.replace(/[^0-9]/g, '');
            
            if (postalCode.length !== 7) {
                showModal('郵便番号は7桁で入力してください。');
                return;
            }
            
            // ローディング状態を表示
            const originalText = postalSearchBtn.textContent;
            postalSearchBtn.textContent = '検索中...';
            postalSearchBtn.disabled = true;
            
            try {
                // 郵便番号API（実装時は実際のAPIに置き換え）
                const response = await fetch(`https://zipcloud.ibsnet.co.jp/api/search?zipcode=${postalCode}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    const result = data.results[0];
                    addressInput.value = `${result.address1}${result.address2}${result.address3}`;
                } else {
                    showModal('該当する住所が見つかりませんでした。', 'info');
                }
            } catch (error) {
                console.error('郵便番号検索エラー:', error);
                showModal('郵便番号検索中にエラーが発生しました。');
            } finally {
                // ローディング状態を解除
                postalSearchBtn.textContent = originalText;
                postalSearchBtn.disabled = false;
            }
        });
    }
    
    async function handleAnalyze() {
        // フォームデータを収集
        const formData = collectFormData();
        
        // バリデーション
        if (!validateStep(1)) {
            showStep(1);
            return;
        }
        
        // 分析画面を表示
        form.style.display = 'none';
        analyzingScreen.style.display = 'block';
        
        // 分析アニメーション開始
        startAnalyzingAnimation();
        
        try {
            // 検索半径を数値に変換
            const radiusMap = {
                '1km': 1000,
                '3km': 3000,
                '5km': 5000
            };
            
            // APIリクエスト用のデータを準備
            const requestData = {
                clinic_info: {
                    name: formData.clinicName,
                    address: formData.address,
                    postal_code: formData.postalCode,
                    departments: formData.departments,
                    features: formData.clinicFeatures
                },
                search_radius: radiusMap[formData.analysisRange] || 3000,
                additional_info: formData.targetPatients
            };
            
            // APIリクエスト
            const response = await fetch('/api/competitive-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '分析に失敗しました');
            }
            
            const result = await response.json();
            
            // 結果を表示
            displayResult(result);
            
        } catch (error) {
            console.error('分析エラー:', error);
            showModal(`分析中にエラーが発生しました: ${error.message}`);
            analyzingScreen.style.display = 'none';
            form.style.display = 'block';
        }
    }
    
    function collectFormData() {
        const departments = Array.from(document.querySelectorAll('input[name="departments"]:checked'))
            .map(cb => cb.value);
        
        return {
            clinicName: document.getElementById('clinic-name').value.trim(),
            postalCode: document.getElementById('postal-code').value.trim(),
            address: document.getElementById('address').value.trim(),
            departments: departments,
            analysisRange: document.querySelector('input[name="analysisRange"]:checked').value,
            clinicFeatures: document.getElementById('clinic-features').value.trim(),
            targetPatients: document.getElementById('target-patients').value.trim()
        };
    }
    
    function startAnalyzingAnimation() {
        const steps = document.querySelectorAll('.step-item');
        const progressFill = document.querySelector('.progress-fill');
        let currentStep = 0;
        
        // アニメーションループ
        const animateStep = () => {
            if (currentStep < steps.length) {
                // 現在のステップをアクティブに
                steps[currentStep].classList.add('active');
                
                // プログレスバーを更新
                const progress = ((currentStep + 1) / steps.length) * 100;
                progressFill.style.width = `${progress}%`;
                
                currentStep++;
                
                // 次のステップへ（2秒後）
                setTimeout(animateStep, 2000);
            }
        };
        
        // アニメーション開始
        setTimeout(animateStep, 500);
    }
    
    // HTMLサニタイズ関数
    function sanitizeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
    
    // カスタムモーダル関数
    function showModal(message, type = 'error') {
        // 既存のモーダルがあれば削除
        const existingModal = document.querySelector('.custom-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.className = 'custom-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-dialog ${type}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${type === 'error' ? 'エラー' : type === 'info' ? '情報' : '確認'}</h3>
                        <button class="modal-close" aria-label="閉じる">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p>${sanitizeHtml(message)}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-primary modal-ok">OK</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // イベントリスナー
        const closeModal = () => {
            modal.classList.add('fade-out');
            setTimeout(() => modal.remove(), 300);
        };
        
        modal.querySelector('.modal-close').addEventListener('click', closeModal);
        modal.querySelector('.modal-ok').addEventListener('click', closeModal);
        modal.querySelector('.modal-backdrop').addEventListener('click', closeModal);
        
        // ESCキーで閉じる
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
        
        // フォーカスをOKボタンに設定
        setTimeout(() => modal.querySelector('.modal-ok').focus(), 100);
    }
    
    // 地図を初期化して競合を表示
    function initMap(result) {
        if (!googleMapsLoaded) {
            console.error('Google Maps not loaded yet');
            return;
        }
        
        const mapContainer = document.getElementById('competitors-map');
        if (!mapContainer) return;
        
        // 中心座標（自院の位置）を設定
        let center = { lat: 35.6762, lng: 139.6503 }; // デフォルト（東京）
        
        // 検索結果の中心座標があれば使用（これが自院の座標）
        if (result.center && result.center.lat && result.center.lng) {
            center = result.center;
        }
        
        // 地図を初期化
        mapInstance = new google.maps.Map(mapContainer, {
            zoom: 14,
            center: center,
            mapTypeControl: false,
            fullscreenControl: false,
            streetViewControl: false
        });
        
        // InfoWindowを初期化
        infoWindow = new google.maps.InfoWindow();
        
        // 自院のマーカーを追加（特別な色）
        const clinicMarker = new google.maps.Marker({
            position: center,
            map: mapInstance,
            title: result.clinic_info.name,
            icon: {
                url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            }
        });
        
        clinicMarker.addListener('click', () => {
            infoWindow.setContent(`
                <div class="map-info-window">
                    <h4>${sanitizeHtml(result.clinic_info.name)}</h4>
                    <p class="info-type">自院</p>
                    <p>${sanitizeHtml(result.clinic_info.address)}</p>
                </div>
            `);
            infoWindow.open(mapInstance, clinicMarker);
        });
        
        // 検索範囲の円を追加
        const searchCircle = new google.maps.Circle({
            strokeColor: '#1890ff',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#1890ff',
            fillOpacity: 0.1,
            map: mapInstance,
            center: center,
            radius: result.search_radius || 3000  // メートル単位
        });
        
        // 競合のマーカーを追加
        result.competitors.forEach((competitor, index) => {
            if (!competitor.location || !competitor.location.lat || !competitor.location.lng) return;
            
            const marker = new google.maps.Marker({
                position: {
                    lat: competitor.location.lat,
                    lng: competitor.location.lng
                },
                map: mapInstance,
                title: competitor.name,
                icon: {
                    url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
                }
            });
            
            // クリック時の情報表示
            marker.addListener('click', () => {
                const ratingStars = competitor.rating ? '★'.repeat(Math.round(competitor.rating)) : '';
                infoWindow.setContent(`
                    <div class="map-info-window">
                        <h4>${sanitizeHtml(competitor.name)}</h4>
                        <p class="info-address">${sanitizeHtml(competitor.formatted_address || competitor.address)}</p>
                        ${competitor.rating ? `<p class="info-rating">${ratingStars} ${sanitizeHtml(String(competitor.rating))} (${sanitizeHtml(String(competitor.user_ratings_total))}件)</p>` : ''}
                        ${competitor.phone_number ? `<p class="info-phone">📞 ${sanitizeHtml(competitor.phone_number)}</p>` : ''}
                        ${competitor.website ? `<p class="info-website"><a href="${sanitizeHtml(competitor.website)}" target="_blank">ウェブサイトを見る</a></p>` : ''}
                        ${competitor.opening_hours?.weekday_text ? `
                            <details class="info-hours">
                                <summary>営業時間</summary>
                                <ul>
                                    ${competitor.opening_hours.weekday_text.map(day => `<li>${sanitizeHtml(day)}</li>`).join('')}
                                </ul>
                            </details>
                        ` : ''}
                    </div>
                `);
                infoWindow.open(mapInstance, marker);
            });
            
            markers.push(marker);
        });
        
        // 円の範囲が表示されるように地図を調整
        const bounds = searchCircle.getBounds();
        mapInstance.fitBounds(bounds);
    }
    
    function displayResult(result) {
        console.log('分析結果:', result);
        console.log('自院の住所:', result.clinic_info.address);
        console.log('APIが返した中心座標:', result.center);
        console.log('競合医院の座標:', result.competitors.map(c => ({name: c.name, location: c.location})));
        
        // Google Maps APIを読み込む
        loadGoogleMapsAPI();
        
        // 結果画面のHTMLを生成
        let competitorsHtml = '';
        if (result.competitors && result.competitors.length > 0) {
            competitorsHtml = result.competitors.map((competitor, index) => `
                <div class="competitor-card">
                    <h4>${index + 1}. ${sanitizeHtml(competitor.name)}</h4>
                    <p class="competitor-address">${sanitizeHtml(competitor.formatted_address || competitor.address)}</p>
                    ${competitor.rating ? `<p class="competitor-rating">評価: ${sanitizeHtml(String(competitor.rating))} ⭐ (${sanitizeHtml(String(competitor.user_ratings_total))}件のレビュー)</p>` : ''}
                    ${competitor.phone_number ? `<p class="competitor-phone">電話: ${sanitizeHtml(competitor.phone_number)}</p>` : ''}
                    ${competitor.website ? `<p class="competitor-website"><a href="${encodeURI(competitor.website)}" target="_blank" rel="noopener noreferrer">ウェブサイト</a></p>` : ''}
                    ${competitor.distance ? `<p class="competitor-distance">距離: ${sanitizeHtml(competitor.distance.toFixed(1))}km</p>` : ''}
                </div>
            `).join('');
        }
        
        let swotHtml = '';
        if (result.swot_analysis) {
            swotHtml = `
                <div class="swot-analysis">
                    <h3>SWOT分析</h3>
                    <div class="swot-grid">
                        <div class="swot-section strengths">
                            <h4>強み (Strengths)</h4>
                            <ul>
                                ${result.swot_analysis.strengths.map(s => `<li>${sanitizeHtml(s)}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="swot-section weaknesses">
                            <h4>弱み (Weaknesses)</h4>
                            <ul>
                                ${result.swot_analysis.weaknesses.map(w => `<li>${sanitizeHtml(w)}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="swot-section opportunities">
                            <h4>機会 (Opportunities)</h4>
                            <ul>
                                ${result.swot_analysis.opportunities.map(o => `<li>${sanitizeHtml(o)}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="swot-section threats">
                            <h4>脅威 (Threats)</h4>
                            <ul>
                                ${result.swot_analysis.threats.map(t => `<li>${sanitizeHtml(t)}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }
        
        let recommendationsHtml = '';
        if (result.strategic_recommendations && result.strategic_recommendations.length > 0) {
            recommendationsHtml = `
                <div class="recommendations">
                    <h3>戦略的提案</h3>
                    ${result.strategic_recommendations.map(rec => `
                        <div class="recommendation-item ${sanitizeHtml(rec.priority)}">
                            <h4>${sanitizeHtml(rec.title)}</h4>
                            <p>${sanitizeHtml(rec.description)}</p>
                            <span class="priority-badge">優先度: ${rec.priority === 'high' ? '高' : rec.priority === 'medium' ? '中' : '低'}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        resultScreen.innerHTML = `
            <div class="result-header">
                <h2>競合分析結果</h2>
                <div class="analysis-summary">
                    <p>分析対象: ${sanitizeHtml(result.clinic_info.name)}</p>
                    <p>検索範囲: 半径${sanitizeHtml(String(result.search_radius / 1000))}km</p>
                    <p>競合数: ${sanitizeHtml(String(result.competitors_found))}件</p>
                    <p>分析日時: ${new Date(result.analysis_date).toLocaleString('ja-JP')}</p>
                </div>
            </div>
            
            <div class="result-content">
                <div class="map-section">
                    <h3>競合マップ</h3>
                    <div id="competitors-map" style="height: 500px; width: 100%; margin-bottom: 2rem;"></div>
                    <div class="map-legend">
                        <p><img src="http://maps.google.com/mapfiles/ms/icons/blue-dot.png" alt="自院" style="width: 20px; vertical-align: middle;"> 自院</p>
                        <p><img src="http://maps.google.com/mapfiles/ms/icons/red-dot.png" alt="競合" style="width: 20px; vertical-align: middle;"> 競合医療機関</p>
                    </div>
                </div>
                
                ${swotHtml}
                ${recommendationsHtml}
                
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="window.print()">印刷</button>
                    <button class="btn btn-secondary" onclick="location.reload()">新しい分析を開始</button>
                    <a href="/user/dashboard" class="btn btn-link">ダッシュボードに戻る</a>
                </div>
            </div>
        `;
        
        analyzingScreen.style.display = 'none';
        resultScreen.style.display = 'block';
        
        // Google Maps APIが読み込まれたら地図を初期化
        if (googleMapsLoaded) {
            setTimeout(() => initMap(result), 100);
        } else {
            // APIの読み込みを待つ
            const checkInterval = setInterval(() => {
                if (googleMapsLoaded) {
                    clearInterval(checkInterval);
                    initMap(result);
                }
            }, 100);
        }
    }
});