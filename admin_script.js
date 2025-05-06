document.addEventListener('DOMContentLoaded', () => {
    console.log("Admin panel JS loaded.");

    // Example: Handle RAG data upload form submission (placeholder)
    const ragForm = document.getElementById('rag-upload-form');
    if (ragForm) {
        ragForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent actual submission for now
            const specialty = document.getElementById('specialty-select').value;
            const fileInput = document.getElementById('rag-file-upload');
            if (specialty && fileInput.files.length > 0) {
                console.log(`Uploading RAG data for ${specialty}:`, fileInput.files[0].name);
                alert(`RAGデータ (${specialty}: ${fileInput.files[0].name}) のアップロード処理（仮）`);
                // TODO: Implement actual file upload logic
            } else {
                alert('診療科を選択し、ファイルを選んでください。');
            }
        });
    }

    // Example: Handle API key addition (placeholder)
    const addApiKeyButton = document.getElementById('add-api-key');
    const apiKeysSection = document.getElementById('api-keys-section');
    let apiKeyCounter = 2; // Start counting from 2 since 1 is already in HTML
    if (addApiKeyButton && apiKeysSection) {
        addApiKeyButton.addEventListener('click', () => {
            const newKeyDiv = document.createElement('div');
            newKeyDiv.innerHTML = `
                <label for="api-key-${apiKeyCounter}">APIキー ${apiKeyCounter}:</label>
                <input type="password" id="api-key-${apiKeyCounter}" name="api_key[]">
                <button type="button" class="remove-api-key">削除</button>
            `;
            // Insert before the 'Add' button
            apiKeysSection.insertBefore(newKeyDiv, addApiKeyButton);
            apiKeyCounter++;
        });
    }

    // Example: Handle API key removal (uses event delegation)
    if (apiKeysSection) {
        apiKeysSection.addEventListener('click', (event) => {
            if (event.target.classList.contains('remove-api-key')) {
                if (confirm('このAPIキーを削除しますか？')) {
                     event.target.closest('div').remove(); 
                     console.log("API key row removed.");
                     // TODO: Add logic to actually remove the key on the backend
                }
            }
        });
    }
    
    // Example: Handle API Settings form submission
    const apiSettingsForm = document.getElementById('api-settings-form');
    if(apiSettingsForm){
        apiSettingsForm.addEventListener('submit', async (event) => { 
            event.preventDefault();
            console.log("Attempting to save API settings...");
            
            const selectedModel = document.getElementById('api-model-select').value;
            const openaiTextKey = document.getElementById('openai-text-api-key').value;
            const openaiImageKey = document.getElementById('openai-image-api-key').value;
            const googleKey = document.getElementById('google-api-key').value;
            const anthropicKey = document.getElementById('anthropic-api-key').value;

            const settings = {
                selected_model: selectedModel,
                api_keys: {
                    openai_text: openaiTextKey,
                    openai_image: openaiImageKey,
                    google: googleKey,
                    anthropic: anthropicKey
                }
            };

            console.log("Sending API settings:", settings);
            const apiStatusMessage = document.getElementById('api-status-message');
            apiStatusMessage.textContent = '保存中...';
            apiStatusMessage.style.color = 'orange';

            try {
                const response = await fetch('/api/admin/settings/api', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(settings),
                });

                const result = await response.json();

                if (response.ok) {
                    apiStatusMessage.textContent = result.message || '設定を保存しました。';
                    apiStatusMessage.style.color = 'green';
                } else {
                    throw new Error(result.error || 'API設定の保存に失敗しました。');
                }
            } catch (error) {
                console.error('Error saving API settings:', error);
                apiStatusMessage.textContent = `エラー: ${error.message}`;
                apiStatusMessage.style.color = 'red';
            }
        });
    }

    // Example: Handle Output Settings form submission (placeholder)
    const outputSettingsForm = document.getElementById('output-settings-form');
    if(outputSettingsForm){
        outputSettingsForm.addEventListener('submit', (event) => {
            event.preventDefault();
            console.log("Saving output settings...");
            alert("出力設定の保存処理（仮）");
             // TODO: Implement actual saving logic
        });
    }

    // Modify Character Limit save logic
    const saveLimitsBtn = document.getElementById('save-limits-btn'); // Use button ID
    const limitsStatusMessage = document.getElementById('limits-status-message'); // Get status element
    const charLimitForm = document.getElementById('char-limit-form'); // Still need the form element

    // Remove the form submit listener
    /* 
    if(charLimitForm){ 
        charLimitForm.addEventListener('submit', async (event) => {
            // ... old submit logic ... 
        });
    }
    */

    // Add click listener to the button instead
    if(saveLimitsBtn && charLimitForm && limitsStatusMessage){
        saveLimitsBtn.addEventListener('click', async () => { // Listen for click
            // event.preventDefault(); // No longer needed for button type="button"
            console.log("Attempting to save character limit settings...");

            const limits = {};
            const inputs = charLimitForm.querySelectorAll('input[type="number"]');
            inputs.forEach(input => {
                const key = input.id.replace('limit-', '');
                limits[key] = input.value; 
            });

            limitsStatusMessage.textContent = '保存中...'; // Show loading message
            limitsStatusMessage.style.color = 'orange';

            try {
                 const apiUrl = '/api/admin/settings/limits'; // Use relative URL
                 const response = await fetch(apiUrl, {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json', },
                     body: JSON.stringify({ limits: limits }), 
                 });
 
                 if (!response.ok) {
                     const errorData = await response.json();
                     throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                 }
 
                 const result = await response.json();
                 console.log("Char limit settings save result:", result);
                 limitsStatusMessage.textContent = result.message || "文字数制限を保存しました。"; // Show success
                 limitsStatusMessage.style.color = 'green';
                 // alert("文字数制限を保存しました。"); // Remove alert
 
             } catch (error) {
                  console.error('Error saving character limit settings:', error);
                  limitsStatusMessage.textContent = `エラー: ${error.message}`; // Show error
                  limitsStatusMessage.style.color = 'red';
                  // const displayError = error.message.includes("Failed to fetch") ? "サーバーへの接続に失敗しました。" : error.message;
                  // alert(`文字数制限の保存中にエラーが発生しました: ${displayError}`); // Remove alert
             }
        });
         console.log("Character limit save button listener added.");
    } else {
        console.warn("Could not find elements needed for character limit saving.");
    }

    // Example: Handle Image Upload form submission (placeholder)
    const imageUploadForm = document.getElementById('image-upload-form');
    if(imageUploadForm){
        imageUploadForm.addEventListener('submit', (event) => {
            event.preventDefault();
             const imageInput = document.getElementById('persona-image-upload');
             if (imageInput.files.length > 0) {
                console.log(`Uploading image: ${imageInput.files[0].name}`);
                alert(`画像 (${imageInput.files[0].name}) のアップロード処理（仮）`);
                // TODO: Implement actual image upload logic
             } else {
                alert('画像ファイルを選んでください。');
             }
        });
    }

    // --- APIキー管理 --- 
    // const apiKeyList = document.getElementById('api-key-list'); // Already handled or unused
    // const addApiKeyButton = document.getElementById('add-api-key'); // Redeclaration removed
    // const apiNameInput = document.getElementById('api-name'); // Unused element
    // const apiKeyInput = document.getElementById('api-key'); // Unused element

    // APIキー追加ボタンの処理 - Already handled by the first addApiKeyButton listener
    /* 
    addApiKeyButton.addEventListener('click', () => { ... }); 
    */

    // APIキー削除ボタンの処理 (イベント委譲) - Already handled by the apiKeysSection listener
    // addDeleteEventListeners(apiKeyList, '.delete-api-key', 'APIキー');


    // --- RAGデータ管理 --- 
    // const ragDataList = document.getElementById('rag-data-list'); // Unused element
    // const uploadRagDataButton = document.getElementById('upload-rag-data'); // Unused element
    // const departmentSelect = document.getElementById('department-select'); // Unused element
    // const ragFileUploadInput = document.getElementById('rag-file-upload'); // Already handled

    // RAGデータアップロードボタンの処理 - Already handled by ragForm listener
    /*
    uploadRagDataButton.addEventListener('click', () => { ... });
    */

    // RAGデータ削除ボタンの処理 (イベント委譲) - Placeholder, list not implemented
    // addDeleteEventListeners(ragDataList, '.delete-rag-data', 'RAGデータ');

    // --- ヘルパー関数 --- 

    // HTMLエスケープ関数
    function escapeHTML(str) {
        return str.replace(/[&<>\'\`\"/]/g, match => {
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

    // APIキーをマスクする関数 (簡易版)
    function maskApiKey(key) {
        if (!key || key.length <= 8) return '********';
        return `${key.substring(0, 4)}******************${key.substring(key.length - 4)}`;
    }

    // 削除ボタンのイベントリスナーを追加する関数 (イベント委譲を使用)
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

    // --- API Key Visibility Toggle --- 
    const apiManagementSection = document.getElementById('api-management');
    if (apiManagementSection) {
        apiManagementSection.addEventListener('click', (event) => {
            if (event.target.classList.contains('toggle-api-key-visibility')) {
                const icon = event.target;
                const targetId = icon.dataset.target;
                const targetInput = document.getElementById(targetId);

                if (targetInput) {
                    const isPassword = targetInput.type === 'password';
                    targetInput.type = isPassword ? 'text' : 'password';

                    // Toggle icon classes instead of text content
                    if (isPassword) {
                        icon.classList.remove('icon-eye-visible');
                        icon.classList.add('icon-eye-hidden');
                    } else {
                        icon.classList.remove('icon-eye-hidden');
                        icon.classList.add('icon-eye-visible');
                    }
                }
            }
        });
        console.log("API Key visibility toggle listener added.");
    } else {
         console.warn("API Management section not found for toggle listener.");
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
                if (currentSettings.selected_text_model) {
                    document.getElementById('text-api-model-select').value = currentSettings.selected_text_model;
                }
                if (currentSettings.api_keys) {
                    document.getElementById('openai-text-api-key').value = currentSettings.api_keys.openai_text || '';
                    document.getElementById('google-api-key').value = currentSettings.api_keys.google || '';
                    document.getElementById('anthropic-api-key').value = currentSettings.api_keys.anthropic || '';
                }

                // Populate Image API Settings
                if (currentSettings.selected_image_model) {
                    document.getElementById('image-api-model-select').value = currentSettings.selected_image_model;
                }
                if (currentSettings.api_keys) {
                    document.getElementById('openai-image-api-key').value = currentSettings.api_keys.openai_image || '';
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

                // Populate Output Settings
                if (currentSettings.output_settings) {
                    document.getElementById('output-pdf').checked = currentSettings.output_settings.pdf;
                    document.getElementById('output-ppt').checked = currentSettings.output_settings.ppt;
                    document.getElementById('output-gslide').checked = currentSettings.output_settings.gslide;
                    console.log("Output settings loaded into form:", currentSettings.output_settings);
                } else {
                    console.warn("Output settings not found in fetched data.");
                }

            } else {
                console.error("Failed to fetch settings:", response.status, await response.text());
            }
        } catch (error) {
            console.error("Error loading settings:", error);
        }
    }

    // Call load settings function
    loadAllSettings();

    // --- Move Save API Settings logic inside DOMContentLoaded ---
    const saveApiSettingsBtn = document.getElementById('save-api-settings-btn');
    const apiStatusMessage = document.getElementById('api-status-message');

    console.log("Checking for save button (inside DOMContentLoaded)..."); // Log 1

    if (saveApiSettingsBtn) {
        console.log("Save API settings button FOUND (inside DOMContentLoaded)."); // Log 2
        saveApiSettingsBtn.addEventListener('click', async () => {
            console.log("Save API settings button CLICKED!"); // Log 3

            // Get Text Settings
            const selectedTextModel = document.getElementById('text-api-model-select').value;
            const openaiTextKey = document.getElementById('openai-text-api-key').value;
            const googleKey = document.getElementById('google-api-key').value;
            const anthropicKey = document.getElementById('anthropic-api-key').value;

            // Get Image Settings
            const selectedImageModel = document.getElementById('image-api-model-select').value;
            const openaiImageKey = document.getElementById('openai-image-api-key').value;


            const settings = {
                selected_text_model: selectedTextModel,
                selected_image_model: selectedImageModel,
                api_keys: {
                    openai_text: openaiTextKey,
                    openai_image: openaiImageKey,
                    google: googleKey,
                    anthropic: anthropicKey
                }
            };

            console.log("Sending API settings (attempt):", settings); // Log 4
            // Restore loading message display
            if (apiStatusMessage) {
                 apiStatusMessage.textContent = '保存中...';
                 apiStatusMessage.style.color = 'orange';
            } else {
                 console.warn("API status message element not found.");
            }

            try {
                console.log("Starting fetch to /api/admin/settings/api"); // Log 5
                const response = await fetch('/api/admin/settings/api', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', },
                    body: JSON.stringify(settings)
                 });
                console.log("Fetch response status:", response.status); // Log 6

                const result = await response.json();

                if (response.ok) {
                    // Use text display for success
                    if(apiStatusMessage) {
                        apiStatusMessage.textContent = result.message || '設定を保存しました。';
                        apiStatusMessage.style.color = 'green';
                    }
                    // alert(result.message || 'API設定を保存しました。'); // Remove alert
                    console.log("API settings saved successfully."); // Log 7
                } else {
                    throw new Error(result.error || 'API設定の保存に失敗しました。');
                }
            } catch (error) {
                console.error('Error saving API settings:', error); // Log 8 (Error case)
                // Use text display for error
                if(apiStatusMessage) {
                    apiStatusMessage.textContent = `エラー: ${error.message}`;
                    apiStatusMessage.style.color = 'red';
                }
                // alert(`API設定の保存中にエラーが発生しました: ${error.message}`); // Remove alert
            }
        });
        console.log("Event listener ATTACHED to save button (inside DOMContentLoaded)."); // Log 9
    } else {
        console.error("Save API settings button NOT FOUND (inside DOMContentLoaded)!"); // Log 10
    }
    // --- End of moved block ---

    const saveOutputBtn = document.getElementById('save-output-settings-btn');
    const outputStatusMessage = document.getElementById('output-status-message');

    if (saveOutputBtn && outputStatusMessage) {
        saveOutputBtn.addEventListener('click', async () => {
            // Ensure any old alert() calls are removed from this function
            console.log("Attempting to save output settings with text status...");

            const outputSettings = {
                pdf: document.getElementById('output-pdf').checked,
                ppt: document.getElementById('output-ppt').checked,
                gslide: document.getElementById('output-gslide').checked
            };

            outputStatusMessage.textContent = '保存中...';
            outputStatusMessage.style.color = 'orange';

            try {
                const apiUrl = '/api/admin/settings/output';
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', },
                    body: JSON.stringify({ output_settings: outputSettings }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                console.log("Output settings save result:", result);
                outputStatusMessage.textContent = result.message || "出力設定を保存しました。";
                outputStatusMessage.style.color = 'green';

            } catch (error) {
                 console.error('Error saving output settings:', error);
                 outputStatusMessage.textContent = `エラー: ${error.message || '不明なエラーが発生しました。'}`;
                 outputStatusMessage.style.color = 'red';
            }
        });
        console.log("Output settings save button listener updated to use text status.");
    } else {
         if (!saveOutputBtn) console.warn("Could not find #save-output-settings-btn");
         if (!outputStatusMessage) console.warn("Could not find #output-status-message");
         console.warn("Output settings save button listener for text status not fully initialized.");
    }

}); 