#用來生成cooldown.pkl檔案

import pickle
from datetime import datetime, timedelta

# 初始冷卻時間數據，確保數據不為空
cooldown = {
    123456789: {  # 替換為實際的用戶ID
        987654321: datetime.now() - timedelta(hours=1)  # 替換為實際的角色ID和冷卻時間
    },
    234567890: {  # 替換為另一個用戶ID
        876543210: datetime.now() - timedelta(hours=2)  # 替換為另一個角色ID和冷卻時間
    }
}

# 保存冷卻時間數據到文件
with open('cooldown.pkl', 'wb') as f:
    pickle.dump(cooldown, f)

print('冷卻時間數據已保存到 cooldown.pkl')
