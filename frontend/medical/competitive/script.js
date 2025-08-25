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
        script.src = `https://maps.googleapis.com/maps/api/js?key=${data.api_key}&callback=onGoogleMapsLoaded&language=ja&region=JP&libraries=geometry`;
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
    
    // 初期化
    init();
    
    async function init() {
        // 診療科チェックボックスを生成（APIから取得）
        await loadAndRenderDepartments();
        
        // イベントリスナーの設定
        setupEventListeners();
        
        // 郵便番号検索機能
        setupPostalCodeSearch();
    }
    
    // 診療科名とアイコンファイル名のマッピング
    // chief_complaints.jsonの診療科名 → 実際のアイコンファイル名
    const departmentIconMap = {
        '歯科': '一般歯科'  // 「歯科」のアイコンは「一般歯科.png」を使用
        // 消化器内科、内分泌科は同名のファイルが存在するのでマッピング不要
    };
    
    async function loadAndRenderDepartments() {
        const container = document.querySelector('.department-checkbox-grid');
        container.innerHTML = '<div style="text-align: center; color: #666;">診療科を読み込み中...</div>';
        
        try {
            // 現在のカテゴリを取得（URLから）
            const pathParts = window.location.pathname.split('/');
            const category = pathParts[1] || 'user';
            
            // すべてのカテゴリから診療科を取得（userの場合）
            let allDepartments = [];
            
            if (category === 'user') {
                // userの場合は全カテゴリの診療科を取得
                const categories = ['medical', 'dental', 'others'];
                for (const cat of categories) {
                    const response = await fetch(`/api/departments/${cat}`);
                    if (response.ok) {
                        const data = await response.json();
                        allDepartments = allDepartments.concat(data.departments);
                    }
                }
            } else {
                // 特定カテゴリの診療科を取得
                const response = await fetch(`/api/departments/${category}`);
                if (response.ok) {
                    const data = await response.json();
                    allDepartments = data.departments;
                }
            }
            
            // 重複を除去
            allDepartments = [...new Set(allDepartments)];
            
            // ラジオボタンをレンダリング（アイコン付き、1つだけ選択可能）
            container.innerHTML = '';
            container.className = 'department-options'; // ペルソナ生成と同じクラス名に変更
            
            allDepartments.forEach((dept, index) => {
                const label = document.createElement('label');
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.id = `dept-${dept}`;
                radio.name = 'department';
                radio.value = dept;
                if (index === 0) radio.required = true;
                
                const icon = document.createElement('div');
                icon.className = 'department-icon';
                
                // アイコンファイル名を決定（マッピングがあれば使用）
                const iconFileName = departmentIconMap[dept] || dept;
                
                // WebP形式を优先して読み込み、フォールバックでPNG
                const webpImg = new Image();
                webpImg.src = `/images/departments/${iconFileName}.webp`;
                webpImg.onload = function() {
                    icon.style.backgroundImage = `url('/images/departments/${iconFileName}.webp')`;
                    icon.style.backgroundSize = 'contain';
                    icon.style.backgroundPosition = 'center';
                    icon.style.backgroundRepeat = 'no-repeat';
                };
                webpImg.onerror = function() {
                    // WebPが読み込めない場合はPNGを試す
                    const pngImg = new Image();
                    pngImg.src = `/images/departments/${iconFileName}.png`;
                    pngImg.onload = function() {
                        icon.style.backgroundImage = `url('/images/departments/${iconFileName}.png')`;
                        icon.style.backgroundSize = 'contain';
                        icon.style.backgroundPosition = 'center';
                        icon.style.backgroundRepeat = 'no-repeat';
                    };
                    pngImg.onerror = function() {
                        // 両方とも読み込めない場合はアイコンを非表示
                        icon.style.display = 'none';
                        label.style.paddingTop = '15px';
                    };
                };
                
                label.appendChild(radio);
                label.appendChild(icon);
                label.appendChild(document.createTextNode(dept));
                
                // 選択状態の変更を監視
                radio.addEventListener('change', function() {
                    // すべてのselectedクラスを削除
                    container.querySelectorAll('label').forEach(l => l.classList.remove('selected'));
                    // 選択されたラベルにselectedクラスを追加
                    if (radio.checked) {
                        label.classList.add('selected');
                    }
                });
                
                container.appendChild(label);
            });
            
        } catch (error) {
            console.error('Failed to load departments:', error);
            container.innerHTML = '<div style="color: red;">診療科の読み込みに失敗しました</div>';
        }
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
                const checkedDept = document.querySelector('input[name="department"]:checked');
                
                if (!clinicName) {
                    showModal('クリニック名を入力してください。');
                    return false;
                }
                
                if (!address) {
                    showModal('住所を入力してください。');
                    return false;
                }
                
                if (!checkedDept) {
                    showModal('診療科を1つ選択してください。');
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
                    department: formData.department,
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
            
            // プログレスバーを100%に
            const progressFill = document.querySelector('.progress-bar-fill');
            const progressPercentage = document.querySelector('.progress-percentage');
            const currentStepElement = document.querySelector('.current-step');
            const estimatedTimeElement = document.querySelector('.estimated-time');
            
            if (progressFill && progressPercentage) {
                progressFill.style.width = '100%';
                progressPercentage.textContent = '100%';
                if (currentStepElement) {
                    currentStepElement.textContent = '分析完了';
                }
                if (estimatedTimeElement) {
                    estimatedTimeElement.textContent = '';
                }
            }
            
            // 少し待ってから結果を表示
            setTimeout(() => {
                displayResult(result);
            }, 500);
            
        } catch (error) {
            console.error('分析エラー:', error);
            showModal(`分析中にエラーが発生しました: ${error.message}`);
            analyzingScreen.style.display = 'none';
            form.style.display = 'block';
        }
    }
    
    function collectFormData() {
        const departmentElement = document.querySelector('input[name="department"]:checked');
        const department = departmentElement ? departmentElement.value : '';
        
        return {
            clinicName: document.getElementById('clinic-name').value.trim(),
            postalCode: document.getElementById('postal-code').value.trim(),
            address: document.getElementById('address').value.trim(),
            department: department,
            analysisRange: document.querySelector('input[name="analysisRange"]:checked').value,
            clinicFeatures: document.getElementById('clinic-features').value.trim(),
            targetPatients: document.getElementById('target-patients').value.trim()
        };
    }
    
    function startAnalyzingAnimation() {
        const progressFill = document.querySelector('.progress-bar-fill');
        const progressPercentage = document.querySelector('.progress-percentage');
        const currentStepElement = document.querySelector('.current-step');
        const estimatedTimeElement = document.querySelector('.estimated-time');
        
        const steps = [
            { text: 'ステップ 1/3: 近隣の医療機関を検索中', time: '予想時間: 約10秒' },
            { text: 'ステップ 2/3: 詳細情報を収集中', time: '予想時間: 約10秒' },
            { text: 'ステップ 3/3: AIがSWOT分析を生成中', time: '予想時間: 約10秒' }
        ];
        
        let currentStep = 0;
        let progress = 0;
        const totalDuration = 30000; // 30秒
        const intervalTime = 300; // 0.3秒ごとに更新（30秒で100回 = 1%ずつ）
        const progressPerStep = 1; // 1%ずつ増加
        
        // プログレスバーのスムーズなアニメーション
        const animateProgress = () => {
            progress = Math.min(100, progress + progressPerStep);
            
            progressFill.style.width = `${progress}%`;
            progressPercentage.textContent = `${Math.round(progress)}%`;
            
            // ステップの更新
            const stepIndex = Math.floor((progress / 100) * steps.length);
            if (stepIndex !== currentStep && stepIndex < steps.length) {
                currentStep = stepIndex;
                currentStepElement.textContent = steps[currentStep].text;
                estimatedTimeElement.textContent = steps[currentStep].time;
            }
            
            // 100%未満の場合は続行
            if (progress < 100) {
                setTimeout(animateProgress, intervalTime);
            }
        };
        
        // アニメーション開始
        setTimeout(animateProgress, 300);
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
            streetViewControl: false,
            gestureHandling: 'cooperative'  // CTRLキーでズーム（デフォルト）
        });
        
        // InfoWindowを初期化
        infoWindow = new google.maps.InfoWindow();
        
        // スクロール通知を非表示にする
        google.maps.event.addListenerOnce(mapInstance, 'idle', function() {
            // 地図が読み込まれた後、通知要素を探して非表示にする
            const observer = new MutationObserver(function(mutations) {
                const scrollNotice = mapContainer.querySelector('.gm-style-pbc');
                if (scrollNotice) {
                    scrollNotice.style.display = 'none';
                }
                
                // より一般的なセレクタも試す
                const notices = mapContainer.querySelectorAll('[style*="opacity"]');
                notices.forEach(notice => {
                    if (notice.textContent && notice.textContent.includes('Ctrl') || notice.textContent.includes('スクロール')) {
                        notice.style.display = 'none';
                    }
                });
            });
            
            observer.observe(mapContainer, {
                childList: true,
                subtree: true
            });
        });
        
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
            
            // 距離を計算（デバッグ用）
            const distance = google.maps.geometry.spherical.computeDistanceBetween(
                new google.maps.LatLng(center.lat, center.lng),
                new google.maps.LatLng(competitor.location.lat, competitor.location.lng)
            );
            // console.log(`${competitor.name}: ${Math.round(distance)}m (範囲: ${result.search_radius}m)`);
            
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
        // console.log('分析結果:', result);
        // console.log('自院の住所:', result.clinic_info.address);
        // console.log('APIが返した中心座標:', result.center);
        // console.log('競合医院の座標:', result.competitors.map(c => ({name: c.name, location: c.location})));
        
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
                    <a href="/medical/" class="btn btn-link">ダッシュボードに戻る</a>
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