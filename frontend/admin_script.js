function loadSettings() {
    fetch('/api/admin/settings')
        .then(response => response.json())
        .then(settings => {
            // モデル設定の読み込み
            if (settings.models) {
                if (settings.models.text_api_model) {
                    document.getElementById('textModelSelect').value = settings.models.text_api_model;
                }
                // 画像モデル設定の読み込みを追加
                if (settings.models.image_api_model) {
                    document.getElementById('imageModelSelect').value = settings.models.image_api_model;
                } else {
                    document.getElementById('imageModelSelect').value = ""; // デフォルトは「画像生成なし」
                }
            }

            // 文字数制限設定の読み込み
            if (settings.limits) {
                for (const key in settings.limits) {
                    const inputElement = document.getElementById(key + 'Limit');
                    if (inputElement) {
                        inputElement.value = settings.limits[key];
                    }
                }
            }
        })
        .catch(error => console.error('Error loading settings:', error));
}

function saveModelSettings() {
    const selectedTextModel = document.getElementById('textModelSelect').value;
    const selectedImageModel = document.getElementById('imageModelSelect').value;

    console.log("Saving model settings:", { text_api_model: selectedTextModel, image_api_model: selectedImageModel });

    fetch('/api/admin/settings/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text_api_model: selectedTextModel,
            image_api_model: selectedImageModel
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail || 'Failed to save model settings'); });
        }
        return response.json();
    })
    .then(data => {
        console.log('Model settings saved:', data);
        alert('モデル設定が保存されました。');
        loadSettings(); // 設定を再読み込みしてUIに反映
    })
    .catch(error => {
        console.error('Error saving model settings:', error);
        alert('モデル設定の保存に失敗しました: ' + error.message);
    });
} 