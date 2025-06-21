import shutil
import os
from datetime import datetime
import pandas as pd

class BackupSystem:
    def __init__(self, excel_path='Base_financas.xlsx'):
        self.excel_path = excel_path
        self.backup_dir = 'backups'
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Cria o diretório de backup se não existir"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, operation_type="manual"):
        """Cria um backup do arquivo Excel"""
        try:
            if not os.path.exists(self.excel_path):
                return False, "Arquivo principal não encontrado"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{operation_type}_{timestamp}.xlsx"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(self.excel_path, backup_path)
            return True, backup_path
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}"
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        try:
            if not os.path.exists(self.backup_dir):
                return []
            
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.xlsx') and file.startswith('backup_'):
                    file_path = os.path.join(self.backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backups.append({
                        'filename': file,
                        'path': file_path,
                        'size': file_size,
                        'date': file_date
                    })
            
            return sorted(backups, key=lambda x: x['date'], reverse=True)
        except Exception as e:
            return []
    
    def restore_backup(self, backup_path):
        """Restaura um backup específico"""
        try:
            if not os.path.exists(backup_path):
                return False, "Backup não encontrado"
            
            # Cria backup do estado atual antes de restaurar
            self.create_backup("before_restore")
            
            # Restaura o backup
            shutil.copy2(backup_path, self.excel_path)
            return True, "Backup restaurado com sucesso"
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def cleanup_old_backups(self, keep_last=10):
        """Remove backups antigos, mantendo apenas os últimos N"""
        try:
            backups = self.list_backups()
            if len(backups) > keep_last:
                for backup in backups[keep_last:]:
                    os.remove(backup['path'])
                return True, f"Removidos {len(backups) - keep_last} backups antigos"
            return True, "Nenhum backup removido"
        except Exception as e:
            return False, f"Erro ao limpar backups: {str(e)}"

# Função para uso no dashboard
def safe_backup(operation_type="manual"):
    """Função segura para criar backup"""
    backup_sys = BackupSystem()
    success, message = backup_sys.create_backup(operation_type)
    if success:
        # Limpa backups antigos automaticamente
        backup_sys.cleanup_old_backups()
    return success, message 