document.addEventListener('DOMContentLoaded', () => {
    console.log("Admin panel JS loaded.");

    // RAG data upload form submission
    const ragForm = document.getElementById('rag-upload-form');
    const ragStatusMessage = document.getElementById('rag-status-message');
    const ragDataList = document.getElementById('rag-data-list');
    
    if (ragForm) {
        ragForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const specialty = document.getElementById('specialty-select').value;
            const fileInput = document.getElementById('rag-file-upload');
            
            if (!specialty || fileInput.files.length === 0) {
                alert('診療科を選択し、ファイルを選んでください。');
                return;
            }
            
            const formData = new FormData();
            formData.append('specialty', specialty);
            formData.append('file', fileInput.files[0]);
            
            if (ragStatusMessage) {
                ragStatusMessage.textContent = 'アップロード中...';
                ragStatusMessage.style.color = 'orange';
            }
            
            try {
                const response = await fetch('/api/admin/rag/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    if (ragStatusMessage) {
                        ragStatusMessage.textContent = `${result.message} (${result.inserted_count}件のデータを登録)`;
                        ragStatusMessage.style.color = 'green';
                    }
                    
                    // フォームをリセット
                    ragForm.reset();
                    
                    // RAGデータ一覧を更新
                    await loadRAGDataList();
                } else {
                    throw new Error(result.detail || 'RAGデータのアップロードに失敗しました。');
                }
            } catch (error) {
                console.error('Error uploading RAG data:', error);
                if (ragStatusMessage) {
                    ragStatusMessage.textContent = `エラー: ${error.message}`;
                    ragStatusMessage.style.color = 'red';
                }
            }
        });
    }
    
    // RAGデータ一覧の読み込み
    async function loadRAGDataList() {
        if (!ragDataList) return;
        
        try {
            const response = await fetch('/api/admin/rag/tables');
            if (response.ok) {
                const data = await response.json();
                displayRAGDataList(data);
            } else {
                console.error('Failed to load RAG data list');
            }
        } catch (error) {
            console.error('Error loading RAG data list:', error);
        }
    }
    
    // RAGデータ一覧の表示
    function displayRAGDataList(ragData) {
        if (!ragDataList) return;
        
        ragDataList.innerHTML = '';
        
        if (ragData.length === 0) {
            ragDataList.innerHTML = '<tr><td colspan="5" style="text-align: center;">登録されたRAGデータはありません</td></tr>';
            return;
        }
        
        ragData.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${escapeHTML(item.table_name)}</td>
                <td>-</td>
                <td>${item.row_count}</td>
                <td>${item.created_at ? new Date(item.created_at).toLocaleString('ja-JP') : '-'}</td>
                <td>
                    <button class="delete-rag-btn" data-table="${escapeHTML(item.table_name)}">削除</button>
                </td>
            `;
            ragDataList.appendChild(row);
        });
        
        // 削除ボタンのイベントリスナー追加
        document.querySelectorAll('.delete-rag-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const tableName = e.target.dataset.table;
                if (confirm(`テーブル「${tableName}」を削除しますか？`)) {
                    await deleteRAGData(tableName);
                }
            });
        });
    }
    
    // RAGデータの削除
    async function deleteRAGData(tableName) {
        try {
            const response = await fetch(`/api/admin/rag/tables/${encodeURIComponent(tableName)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                if (ragStatusMessage) {
                    ragStatusMessage.textContent = result.message;
                    ragStatusMessage.style.color = 'green';
                }
                await loadRAGDataList();
            } else {
                throw new Error(result.detail || 'RAGデータの削除に失敗しました。');
            }
        } catch (error) {
            console.error('Error deleting RAG data:', error);
            if (ragStatusMessage) {
                ragStatusMessage.textContent = `エラー: ${error.message}`;
                ragStatusMessage.style.color = 'red';
            }
        }
    }

    // Example: Handle API Model Selection Save
    const saveApiSettingsBtn = document.getElementById('save-api-settings-btn');
    const apiStatusMessage = document.getElementById('api-status-message');

    if (saveApiSettingsBtn && apiStatusMessage) {
        saveApiSettingsBtn.addEventListener('click', async () => { 
            console.log("Attempting to save API model selection settings...");

            const selectedTextModel = document.getElementById('text-api-model-select').value;
            const selectedImageModel = document.getElementById('image-api-model-select').value;

            const settings = {
                text_api_model: selectedTextModel,
                image_api_model: selectedImageModel
            };

            console.log("Sending API model selection settings:", settings);
            apiStatusMessage.textContent = '保存中...';
            apiStatusMessage.style.color = 'orange';

            try {
                // エンドポイントURLはバックエンドの実装に合わせてください
                const response = await fetch('/api/admin/settings/models', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(settings),
                });

                const result = await response.json();

                if (response.ok) {
                    apiStatusMessage.textContent = result.message || 'モデル設定を保存しました。';
                    apiStatusMessage.style.color = 'green';
                } else {
                    throw new Error(result.error || 'モデル設定の保存に失敗しました。');
                }
            } catch (error) {
                console.error('Error saving API model selection settings:', error);
                apiStatusMessage.textContent = `エラー: ${error.message}`;
                apiStatusMessage.style.color = 'red';
            }
        });
    }

    // Output Settings form submission logic was here, now removed.

    // Modify Character Limit save logic
    const saveLimitsBtn = document.getElementById('save-limits-btn'); // Use button ID
    const limitsStatusMessage = document.getElementById('limits-status-message'); // Get status element
    const charLimitForm = document.getElementById('char-limit-form'); // Still need the form element
    
    // Add real-time validation for character limit inputs
    if (charLimitForm) {
        const inputs = charLimitForm.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                const value = parseInt(input.value);
                const min = parseInt(input.min) || 50;
                const max = parseInt(input.max) || 200;
                
                if (!isNaN(value) && value >= min && value <= max) {
                    input.style.borderColor = '#28a745';
                    input.style.backgroundColor = '#fff';
                } else {
                    input.style.borderColor = '#dc3545';
                    input.style.backgroundColor = '#fff5f5';
                }
            });
        });
    }

    if(saveLimitsBtn && charLimitForm && limitsStatusMessage){
        saveLimitsBtn.addEventListener('click', async () => { // Listen for click
            console.log("Attempting to save character limit settings...");
            
            // Error message element
            const errorDiv = document.getElementById('char-limit-error');
            console.log('Error div element:', errorDiv);

            // Validate inputs
            const limits = {};
            const inputs = charLimitForm.querySelectorAll('input[type="number"]');
            let hasError = false;
            let errorMessages = [];

            inputs.forEach(input => {
                const key = input.id.replace('limit-', '');
                const value = parseInt(input.value);
                const min = parseInt(input.min) || 50;
                const max = parseInt(input.max) || 200;
                const label = input.parentElement.querySelector('label').textContent.replace(':', '');
                
                console.log(`Validating ${key}: value=${value}, min=${min}, max=${max}`);
                
                if (input.value === '' || isNaN(value)) {
                    hasError = true;
                    errorMessages.push(`${label}を入力してください。`);
                } else if (value < min || value > max) {
                    hasError = true;
                    errorMessages.push(`${label}は${min}〜${max}文字の範囲で入力してください。`);
                } else {
                    limits[key] = String(value); // Convert to string as backend expects
                }
            });

            // Show error if validation failed
            if (hasError) {
                errorDiv.textContent = errorMessages.join(' ');
                errorDiv.style.display = 'block';
                limitsStatusMessage.textContent = '';
                return;
            }

            // Hide error message
            errorDiv.style.display = 'none';
            limitsStatusMessage.textContent = '保存中...'; // Show loading message
            limitsStatusMessage.style.color = 'orange';
            
            // Debug: Log the data being sent
            console.log('Sending limits data:', { limits: limits });
            console.log('JSON stringified:', JSON.stringify({ limits: limits }));

            try {
                 const apiUrl = '/api/admin/settings/char-limits'; // Use relative URL
                 const response = await fetch(apiUrl, {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json', },
                     body: JSON.stringify({ limits: limits }), 
                 });
 
                 if (!response.ok) {
                     const errorData = await response.json();
                     console.error('Error response data:', errorData);
                     throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
                 }
 
                 const result = await response.json();
                 console.log("Char limit settings save result:", result);
                 limitsStatusMessage.textContent = result.message || "文字数制限を保存しました。"; // Show success
                 limitsStatusMessage.style.color = 'green';
 
             } catch (error) {
                  console.error('Error saving character limit settings:', error);
                  limitsStatusMessage.textContent = `エラー: ${error.message}`; // Show error
                  limitsStatusMessage.style.color = 'red';
             }
        });
         console.log("Character limit save button listener added.");
    } else {
        console.warn("Could not find elements needed for character limit saving.");
    }

    // Example: Handle Image Upload form submission (placeholder)
    // This might belong to a different part of the admin or user interface
    // const imageUploadForm = document.getElementById('image-upload-form');
    // if(imageUploadForm){
    //     imageUploadForm.addEventListener('submit', (event) => {
    //         event.preventDefault();
    //          const imageInput = document.getElementById('persona-image-upload');
    //          if (imageInput.files.length > 0) {
    //             console.log(`Uploading image: ${imageInput.files[0].name}`);
    //             alert(`画像 (${imageInput.files[0].name}) のアップロード処理（仮）`);
    //             // TODO: Implement actual image upload logic
    //          } else {
    //             alert('画像ファイルを選んでください。');
    //          }
    //     });
    // }

    // --- Helper Functions (kept for potential future use, or can be removed if truly unused) ---

    function escapeHTML(str) {
        return str.replace(/[&<>\'`\"/]/g, match => {
            const escape = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;',
                '`': '&#x60;',
                '/': '&#x2F;'
            };
            return escape[match];
        });
    }

    function maskApiKey(key) { // This function is no longer used as API keys are not handled in UI
        if (!key || key.length <= 8) return '********';
        return `${key.substring(0, 4)}******************${key.substring(key.length - 4)}`;
    }

    function addDeleteEventListeners(listElement, buttonSelector, itemType) {
        if (!listElement) return;
        listElement.addEventListener('click', (event) => {
            if (event.target.matches(buttonSelector)) {
                const row = event.target.closest('tr');
                if (!row) return;
                const identifier = row.cells[0]?.textContent || '不明なアイテム';
                console.log(`${itemType}削除ボタンクリック: ${identifier}`);
                if (confirm(`${itemType}「${identifier}」を削除しますか？ (バックエンド処理未実装)`)) {
                    row.remove();
                }
            }
        });
    }

    // Load settings function definition
    async function loadAllSettings() {
        console.log("Loading settings from backend...");
        try {
            const response = await fetch('/api/admin/settings');
            if (response.ok) {
                const currentSettings = await response.json();
                console.log("Received settings:", currentSettings);

                // Populate Text API Settings
                if (currentSettings.models && currentSettings.models.text_api_model) {
                    document.getElementById('text-api-model-select').value = currentSettings.models.text_api_model;
                }

                // Populate Image API Settings
                if (currentSettings.models && currentSettings.models.image_api_model) {
                    document.getElementById('image-api-model-select').value = currentSettings.models.image_api_model;
                }

                // Populate Character Limits
                if (currentSettings.limits) {
                    const limitForm = document.getElementById('char-limit-form');
                    if (limitForm) {
                        for (const [key, value] of Object.entries(currentSettings.limits)) {
                            const inputElement = limitForm.querySelector(`#limit-${key}`);
                            if (inputElement) {
                                inputElement.value = value || '';
                            }
                        }
                    }
                }
                // Output settings population logic removed
            } else {
                console.error("Failed to fetch settings:", response.status, await response.text());
            }
        } catch (error) {
            console.error("Error loading settings:", error);
        }
    }

    // Call load settings function
    loadAllSettings();
    
    // Load RAG data list on page load
    loadRAGDataList();

    // saveOutputBtn and outputStatusMessage related logic removed

}); 