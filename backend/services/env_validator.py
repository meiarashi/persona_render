"""
環境変数バリデーター
起動時に必要な環境変数をチェックし、ログに記録
"""

import os
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """環境変数の検証と状態レポート"""
    
    @staticmethod
    def validate() -> Tuple[bool, Dict[str, str]]:
        """
        環境変数をチェックし、結果を返す
        
        Returns:
            (すべての必須変数が存在するか, 状態レポート)
        """
        # 必須環境変数
        required_vars = {
            "OPENAI_API_KEY": "ペルソナ生成、SWOT分析に必要",
            "GOOGLE_MAPS_API_KEY": "競合検索に必要"
        }
        
        # オプション環境変数
        optional_vars = {
            "SERPAPI_KEY": "Web検索による競合詳細情報取得",
            "ESTAT_API_KEY": "地域統計データ取得",
            "ANTHROPIC_API_KEY": "Claude利用時",
            "GOOGLE_API_KEY": "Gemini利用時"
        }
        
        # 認証関連（少なくとも1つは必須）
        auth_vars = {
            "ADMIN_USERNAME": "管理画面アクセス",
            "ADMIN_PASSWORD": "管理画面アクセス",
            "USER_USERNAME": "ユーザー画面アクセス",
            "USER_PASSWORD": "ユーザー画面アクセス"
        }
        
        report = {
            "required": {},
            "optional": {},
            "auth": {},
            "warnings": [],
            "errors": []
        }
        
        all_valid = True
        
        # 必須変数チェック
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                # APIキーの最初の4文字と長さを表示（セキュリティ考慮）
                masked = f"{value[:4]}...({len(value)}文字)" if len(value) > 4 else "設定済み"
                report["required"][var] = f"✓ {masked} - {description}"
                logger.info(f"[ENV] {var}: 設定済み ({description})")
            else:
                report["required"][var] = f"✗ 未設定 - {description}"
                report["errors"].append(f"{var}が設定されていません。{description}")
                logger.error(f"[ENV] {var}: 未設定 ({description})")
                all_valid = False
        
        # オプション変数チェック
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                masked = f"{value[:4]}...({len(value)}文字)" if len(value) > 4 else "設定済み"
                report["optional"][var] = f"✓ {masked} - {description}"
                logger.info(f"[ENV] {var}: 設定済み ({description})")
            else:
                report["optional"][var] = f"- 未設定 - {description}"
                report["warnings"].append(f"{var}未設定: {description}が利用できません")
                logger.warning(f"[ENV] {var}: 未設定 ({description})")
        
        # 認証変数チェック
        auth_count = 0
        for var, description in auth_vars.items():
            value = os.getenv(var)
            if value:
                report["auth"][var] = f"✓ 設定済み - {description}"
                auth_count += 1
            else:
                report["auth"][var] = f"- 未設定 - {description}"
        
        if auth_count == 0:
            report["errors"].append("認証情報が1つも設定されていません")
            logger.error("[ENV] 認証情報が未設定です")
            all_valid = False
        
        # 機能の利用可能性をチェック
        feature_status = {
            "基本的なペルソナ生成": "✓" if os.getenv("OPENAI_API_KEY") else "✗",
            "競合検索": "✓" if os.getenv("GOOGLE_MAPS_API_KEY") else "✗",
            "競合詳細分析": "✓" if os.getenv("SERPAPI_KEY") else "△ (基本機能のみ)",
            "地域統計分析": "✓" if os.getenv("ESTAT_API_KEY") else "△ (デフォルト値使用)",
            "Claude利用": "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗",
            "Gemini利用": "✓" if os.getenv("GOOGLE_API_KEY") else "✗"
        }
        
        report["features"] = feature_status
        
        # サマリー
        if all_valid:
            report["summary"] = "✓ すべての必須環境変数が設定されています"
            logger.info("[ENV] 環境変数チェック完了: すべて正常")
        else:
            report["summary"] = f"✗ {len(report['errors'])}個のエラーがあります"
            logger.error(f"[ENV] 環境変数チェック完了: {len(report['errors'])}個のエラー")
        
        return all_valid, report
    
    @staticmethod
    def print_report(report: Dict[str, str]) -> str:
        """レポートを整形して文字列として返す"""
        output = []
        output.append("=" * 60)
        output.append("環境変数設定状況レポート")
        output.append("=" * 60)
        
        output.append("\n【必須変数】")
        for var, status in report["required"].items():
            output.append(f"  {status}")
        
        output.append("\n【オプション変数】")
        for var, status in report["optional"].items():
            output.append(f"  {status}")
        
        output.append("\n【認証設定】")
        for var, status in report["auth"].items():
            output.append(f"  {status}")
        
        output.append("\n【機能利用可能性】")
        for feature, status in report["features"].items():
            output.append(f"  {status} {feature}")
        
        if report["warnings"]:
            output.append("\n【警告】")
            for warning in report["warnings"]:
                output.append(f"  ⚠ {warning}")
        
        if report["errors"]:
            output.append("\n【エラー】")
            for error in report["errors"]:
                output.append(f"  ✗ {error}")
        
        output.append("\n" + "=" * 60)
        output.append(f"ステータス: {report['summary']}")
        output.append("=" * 60)
        
        return "\n".join(output)
    
    @staticmethod
    def check_and_report():
        """環境変数をチェックしてレポートを出力"""
        is_valid, report = EnvironmentValidator.validate()
        report_str = EnvironmentValidator.print_report(report)
        
        # コンソールに出力
        print(report_str)
        
        # ログファイルにも記録
        for line in report_str.split("\n"):
            if line.strip():
                logger.info(line)
        
        return is_valid, report

# 起動時に自動実行される場合
if __name__ == "__main__":
    EnvironmentValidator.check_and_report()