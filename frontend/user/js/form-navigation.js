// フォームナビゲーションモジュール

const FormNavigation = {
    currentStep: 1,
    totalSteps: 5,
    
    // ステップを表示
    showStep: function(stepNumberToShow) {
        console.log("[DEBUG] Entering showStep function with stepNumberToShow =", stepNumberToShow);
        
        const allSteps = document.querySelectorAll('.form-step');
        console.log("[DEBUG] Found", allSteps.length, "total steps");
        
        allSteps.forEach((step, index) => {
            const stepNum = parseInt(step.getAttribute('data-step'));
            console.log("[DEBUG] Step", index + 1, "has data-step =", stepNum);
            
            if (stepNum === stepNumberToShow) {
                step.classList.add('active');
                console.log("[DEBUG] Activated step", stepNum);
            } else {
                step.classList.remove('active');
            }
        });
        
        this.currentStep = stepNumberToShow;
        console.log("[DEBUG] Current step set to:", this.currentStep);
        
        // フォームデータを収集（確認画面用）
        if (stepNumberToShow === 5) {
            const formData = this.getFormData();
            this.populateConfirmationScreen(formData);
        }
        
        // ステップ3でランダム化
        if (stepNumberToShow === 3) {
            if (window.randomizeDetailSettingsFields) {
                window.randomizeDetailSettingsFields();
            }
        }
        
        console.log("[DEBUG] Exiting showStep function");
    },
    
    // フォームデータを収集
    getFormData: function() {
        const form = document.getElementById('multi-step-form');
        const formData = new FormData(form);
        const data = {};
        
        // 部門と目的の値を対応する表示テキストに変換
        const departmentMap = {
            'ophthalmology': '眼科',
            'internal_medicine': '内科',
            'surgery': '外科',
            'pediatrics': '小児科',
            'orthopedics': '整形外科',
            'ent': '耳鼻咽喉科',
            'dermatology': '皮膚科',
            'gynecology': '婦人科',
            'urology': '泌尿器科',
            'psychiatry': '精神科',
            'neurosurgery': '脳神経外科',
            'respiratory': '呼吸器科',
            'cardiology': '循環器科',
            'gastroenterology': '消化器科',
            'nephrology': '腎臓内科',
            'dentistry': '歯科'
        };
        
        const purposeMap = {
            'increase_patients': '患者数を増やす',
            'increase_unit_price': '客単価を増やす',
            'increase_visit_frequency': '来院頻度を増やす'
        };
        
        for (let [key, value] of formData.entries()) {
            if (key === 'department') {
                data[key] = departmentMap[value] || value;
            } else if (key === 'purpose') {
                data[key] = purposeMap[value] || value;
            } else {
                data[key] = value;
            }
        }
        
        return data;
    },
    
    // 確認画面にデータを表示
    populateConfirmationScreen: function(data) {
        const mappings = {
            'department': 'confirm-department',
            'purpose': 'confirm-purpose',
            'setting_type': 'confirm-setting-type',
            'patient_type': 'confirm-patient-type',
            'name': 'confirm-name',
            'gender': 'confirm-gender',
            'age': 'confirm-age',
            'prefecture': 'confirm-prefecture',
            'municipality': 'confirm-municipality',
            'family': 'confirm-family',
            'occupation': 'confirm-occupation',
            'income': 'confirm-income',
            'hobby': 'confirm-hobby',
            'life_events': 'confirm-life-events',
            'motto': 'confirm-motto',
            'concerns': 'confirm-concerns',
            'favorite_person': 'confirm-favorite-person',
            'media_sns': 'confirm-media-sns',
            'personality_keywords': 'confirm-personality-keywords',
            'health_actions': 'confirm-health-actions',
            'holiday_activities': 'confirm-holiday-activities',
            'catchphrase': 'confirm-catchphrase'
        };
        
        // 基本設定タイプの表示名
        const settingTypeLabels = {
            'auto': '詳細を自動生成',
            'custom': '詳細をカスタマイズ',
            'patient_type': '患者タイプを選択'
        };
        
        for (const [key, elementId] of Object.entries(mappings)) {
            const element = document.getElementById(elementId);
            if (element) {
                let displayValue = data[key] || '';
                
                if (key === 'setting_type' && settingTypeLabels[displayValue]) {
                    displayValue = settingTypeLabels[displayValue];
                }
                
                if (key === 'income' && displayValue) {
                    displayValue = displayValue.replace('-', '〜') + '万円';
                }
                
                element.textContent = displayValue || '未設定';
            }
        }
        
        this.updateDynamicFieldsDisplay(data);
    },
    
    // 動的フィールドの表示を更新
    updateDynamicFieldsDisplay: function(data) {
        const dynamicFieldsContainer = document.querySelector('.dynamic-additional-fields');
        if (dynamicFieldsContainer) {
            dynamicFieldsContainer.innerHTML = '';
            
            const additionalFieldNames = data['additional_field_name[]'] || [];
            const additionalFieldValues = data['additional_field_value[]'] || [];
            
            if (Array.isArray(additionalFieldNames)) {
                additionalFieldNames.forEach((name, index) => {
                    if (name && additionalFieldValues[index]) {
                        const fieldDiv = document.createElement('div');
                        fieldDiv.className = 'form-group';
                        fieldDiv.innerHTML = `
                            <label>${name}</label>
                            <p>${additionalFieldValues[index]}</p>
                        `;
                        dynamicFieldsContainer.appendChild(fieldDiv);
                    }
                });
            }
        }
    },
    
    // 次のステップへ
    nextStep: function() {
        if (this.currentStep < this.totalSteps) {
            this.showStep(this.currentStep + 1);
        }
    },
    
    // 前のステップへ
    previousStep: function() {
        if (this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        }
    },
    
    // 特定のステップへジャンプ
    goToStep: function(stepNumber) {
        if (stepNumber >= 1 && stepNumber <= this.totalSteps) {
            this.showStep(stepNumber);
        }
    }
};

// エクスポート
window.FormNavigation = FormNavigation;