// ペルソナ生成APIモジュール

const PersonaGeneration = {
    // プログレスアニメーション関連
    progressAnimationId: null,
    
    // プログレスアニメーション開始
    startProgressAnimation: function() {
        const progressFill = document.querySelector('.progress-bar-fill');
        const progressPercentage = document.querySelector('.progress-percentage');
        const statusText = document.querySelector('.loading-status-text');
        const currentStep = document.querySelector('.loading-step-current');
        const estimatedTime = document.querySelector('.loading-estimated-time');
        
        if (!progressFill || !progressPercentage) return;
        
        let progress = 0;
        const textDuration = 10000; // 10秒（テキスト生成）
        const imageDuration = 30000; // 30秒（画像生成）
        const totalDuration = textDuration + imageDuration;
        
        // リセット
        progressFill.style.width = '0%';
        progressPercentage.textContent = '0%';
        
        const startTime = Date.now();
        
        const updateProgress = () => {
            const elapsed = Date.now() - startTime;
            
            // 連続的な進捗計算（0-95%）
            const continuousProgress = (elapsed / totalDuration) * 95;
            progress = Math.min(continuousProgress, 95);
            
            // フェーズに基づくテキスト更新
            if (elapsed < textDuration) {
                // フェーズ1: テキスト生成
                if (statusText) statusText.textContent = 'ペルソナの詳細を分析しています...';
                if (currentStep) currentStep.textContent = 'ステップ 1/2: AIがペルソナ詳細を生成中';
            } else if (elapsed < totalDuration) {
                // フェーズ2: 画像生成
                if (statusText) statusText.textContent = 'ペルソナ画像を生成しています...';
                if (currentStep) currentStep.textContent = 'ステップ 2/2: AIが画像を生成中';
                
                // 推定時間の更新
                const remainingSeconds = Math.ceil((totalDuration - elapsed) / 1000);
                if (estimatedTime) {
                    if (remainingSeconds > 20) {
                        estimatedTime.textContent = `予想時間: 約${Math.ceil(remainingSeconds / 10) * 10}秒`;
                    } else {
                        estimatedTime.textContent = `予想時間: あと少し...`;
                    }
                }
            }
            
            progressFill.style.width = `${progress}%`;
            progressPercentage.textContent = `${Math.round(progress)}%`;
            
            // アニメーション継続
            if (elapsed < totalDuration && this.progressAnimationId !== null) {
                this.progressAnimationId = requestAnimationFrame(updateProgress);
            }
        };
        
        this.progressAnimationId = requestAnimationFrame(updateProgress);
    },
    
    // プログレスアニメーション完了
    completeProgressAnimation: function() {
        // 進行中のアニメーションを停止
        if (this.progressAnimationId) {
            cancelAnimationFrame(this.progressAnimationId);
            this.progressAnimationId = null;
        }
        
        const progressFill = document.querySelector('.progress-bar-fill');
        const progressPercentage = document.querySelector('.progress-percentage');
        const statusText = document.querySelector('.loading-status-text');
        
        if (progressFill && progressPercentage) {
            progressFill.style.width = '100%';
            progressPercentage.textContent = '100%';
            if (statusText) statusText.textContent = '完了しました！';
        }
    },
    
    // プログレスアニメーション停止（エラー時）
    stopProgressAnimation: function() {
        if (this.progressAnimationId) {
            cancelAnimationFrame(this.progressAnimationId);
            this.progressAnimationId = null;
        }
    },
    
    // ペルソナ生成API呼び出し
    generatePersona: async function(formData) {
        // ローディング画面を表示
        document.getElementById('multi-step-form').style.display = 'none';
        document.getElementById('loading-screen').style.display = 'flex';
        
        // プログレスアニメーション開始
        this.startProgressAnimation();
        
        try {
            const response = await fetch('/api/generate_persona', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // プログレスアニメーション完了
            this.completeProgressAnimation();
            
            // 結果を表示
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
                document.getElementById('result-screen').style.display = 'block';
                
                if (window.populateResults) {
                    window.populateResults(result);
                }
            }, 500);
            
        } catch (error) {
            console.error('Error generating persona:', error);
            
            // プログレスアニメーション停止
            this.stopProgressAnimation();
            
            // エラー表示
            alert('ペルソナの生成中にエラーが発生しました。もう一度お試しください。');
            
            // フォームに戻る
            document.getElementById('loading-screen').style.display = 'none';
            document.getElementById('multi-step-form').style.display = 'block';
            
            if (window.FormNavigation) {
                window.FormNavigation.showStep(5);
            }
        }
    },
    
    // PDF生成
    generatePDF: async function(personaData) {
        try {
            const response = await fetch('/api/generate_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(personaData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const blob = await response.blob();
            return blob;
            
        } catch (error) {
            console.error('Error generating PDF:', error);
            throw error;
        }
    }
};

// エクスポート
window.PersonaGeneration = PersonaGeneration;