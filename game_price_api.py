# game_price_api.py
import requests
import re
from urllib.parse import quote
import streamlit as st

class GamePriceAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def clean_game_name(self, game_name):
        """게임명 정리 및 표준화"""
        # 특수문자 및 불필요한 텍스트 제거
        clean_name = re.sub(r'[™®©]', '', game_name)
        clean_name = re.sub(r'\s*:\s*.*$', '', clean_name)  # 부제목 제거
        clean_name = re.sub(r'\s*\(.*?\)', '', clean_name)  # 괄호 내용 제거
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        # 일반적인 게임명 별칭 처리 (대폭 확장됨)
        aliases = {
            # 기존 게임들
            'stardew valley': 'Stardew Valley',
            'among us': 'Among Us',
            'fall guys': 'Fall Guys',
            'it takes two': 'It Takes Two',
            'minecraft': 'Minecraft',
            'terraria': 'Terraria',
            'portal 2': 'Portal 2',
            'rocket league': 'Rocket League',
            'overwatch': 'Overwatch 2',
            'csgo': 'Counter-Strike 2',
            'counter strike': 'Counter-Strike 2',
            'gta 5': 'Grand Theft Auto V',
            'gta v': 'Grand Theft Auto V',
            
            # Journey - Steam에 있음 (2019년 출시)
            'journey': 'Journey',
            
            # Overcooked 시리즈
            'overcooked': 'Overcooked',
            'overcooked 2': 'Overcooked! 2',
            'overcook 2': 'Overcooked! 2',
            'overcook2': 'Overcooked! 2',
            'overcooked2': 'Overcooked! 2',
            'overcooked all you can eat': 'Overcooked! All You Can Eat',
            
            # 액션 게임들
            'cuphead': 'Cuphead',
            'hollow knight': 'Hollow Knight',
            'celeste': 'Celeste',
            'hades': 'Hades',
            'disco elysium': 'Disco Elysium',
            'cyberpunk 2077': 'Cyberpunk 2077',
            'elden ring': 'ELDEN RING',
            'dark souls': 'Dark Souls',
            'dark souls 3': 'DARK SOULS III',
            'sekiro': 'Sekiro: Shadows Die Twice',
            'devil may cry 5': 'Devil May Cry 5',
            'doom eternal': 'DOOM Eternal',
            
            # RPG 게임들
            'the witcher 3': 'The Witcher 3: Wild Hunt',
            'witcher 3': 'The Witcher 3: Wild Hunt',
            'baldurs gate 3': "Baldur's Gate 3",
            'baldur\'s gate 3': "Baldur's Gate 3",
            'divinity original sin 2': 'Divinity: Original Sin 2',
            'persona 5': 'Persona 5 Royal',
            'skyrim': 'The Elder Scrolls V: Skyrim',
            'mass effect': 'Mass Effect Legendary Edition',
            
            # 멀티플레이어 게임들
            'valorant': 'VALORANT',
            'league of legends': 'League of Legends',
            'lol': 'League of Legends',
            'apex legends': 'Apex Legends',
            'rainbow six siege': 'Tom Clancy\'s Rainbow Six Siege',
            'r6': 'Tom Clancy\'s Rainbow Six Siege',
            'call of duty': 'Call of Duty: Modern Warfare II',
            'cod': 'Call of Duty: Modern Warfare II',
            
            # 협동 게임들
            'a way out': 'A Way Out',
            'human fall flat': 'Human: Fall Flat',
            'gang beasts': 'Gang Beasts',
            'moving out': 'Moving Out',
            'left 4 dead 2': 'Left 4 Dead 2',
            'l4d2': 'Left 4 Dead 2',
            'deep rock galactic': 'Deep Rock Galactic',
            
            # 전략/시뮬레이션 게임들
            'civilization 6': 'Sid Meier\'s Civilization VI',
            'civ 6': 'Sid Meier\'s Civilization VI',
            'age of empires 4': 'Age of Empires IV',
            'cities skylines': 'Cities: Skylines',
            'planet coaster': 'Planet Coaster',
            'sims 4': 'The Sims 4',
            'euro truck simulator 2': 'Euro Truck Simulator 2',
            'ets2': 'Euro Truck Simulator 2',
            'microsoft flight simulator': 'Microsoft Flight Simulator',
            'farming simulator 22': 'Farming Simulator 22',
            
            # 인디 게임들
            'dead cells': 'Dead Cells',
            'ori and the will of the wisps': 'Ori and the Will of the Wisps',
            'katana zero': 'KATANA ZERO',
            'pizza tower': 'Pizza Tower',
            'shovel knight': 'Shovel Knight',
            'baba is you': 'Baba Is You',
            'the witness': 'The Witness',
            'outer wilds': 'Outer Wilds',
            
            # 힐링/아트 게임들
            'abzu': 'ABZÛ',
            'gris': 'GRIS',
            'unpacking': 'Unpacking',
            'spiritfarer': 'Spiritfarer®: Farewell Edition',
            'a short hike': 'A Short Hike',
            'firewatch': 'Firewatch',
            'what remains of edith finch': 'What Remains of Edith Finch',
            'life is strange': 'Life is Strange',
            'night in the woods': 'Night in the Woods'
        }
        
        lower_name = clean_name.lower()
        for alias, official in aliases.items():
            if alias in lower_name:
                return official
                
        return clean_name
    
    def find_best_game_match(self, target_name, items):
        """검색 결과에서 가장 정확한 게임 찾기"""
        target_lower = target_name.lower()
        best_score = 0
        best_match = None
        
        for i, item in enumerate(items[:10]):  # 상위 10개만 확인
            item_name = item.get('name', '').lower()
            
            # 정확도 점수 계산
            score = 0
            
            # 정확히 일치하는 경우
            if target_lower == item_name:
                score = 100
            # 타겟이 아이템명에 포함되는 경우
            elif target_lower in item_name:
                score = 80
            # 아이템명이 타겟에 포함되는 경우
            elif item_name in target_lower:
                score = 60
            # 단어별 매칭
            else:
                target_words = set(target_lower.split())
                item_words = set(item_name.split())
                common_words = target_words.intersection(item_words)
                if common_words:
                    score = len(common_words) / max(len(target_words), len(item_words)) * 50
            
            if score > best_score:
                best_score = score
                best_match = item
                
        # 최소 점수 이상인 경우만 반환
        return best_match if best_score >= 30 else None
    
    def get_steam_app_id(self, game_name):
        """Steam에서 게임 이름으로 앱 ID 찾기 (정확도 개선)"""
        try:
            # 게임명 정리 (특수문자, 부제목 등 제거)
            clean_name = self.clean_game_name(game_name)
            
            # 여러 검색어로 시도
            search_terms = [clean_name]
            
            # 원본 이름도 추가
            if clean_name != game_name:
                search_terms.append(game_name)
            
            # 공백 제거한 버전도 추가
            if ' ' in clean_name:
                search_terms.append(clean_name.replace(' ', ''))
            
            for term in search_terms:
                search_url = f"https://store.steampowered.com/api/storesearch/?term={quote(term)}&l=korean&cc=kr"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    if items:
                        # 정확한 매칭을 위한 점수 계산
                        best_match = self.find_best_game_match(term, items)
                        if best_match:
                            return best_match['id']
                            
        except Exception as e:
            st.warning(f"Steam 검색 중 오류: {str(e)}")
        return None
    
    def get_steam_price(self, app_id):
        """Steam 게임 가격 조회 (개선됨)"""
        try:
            price_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=kr&l=korean&filters=price_overview"
            response = self.session.get(price_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                app_data = data.get(str(app_id), {})
                
                if not app_data.get('success', False):
                    return None
                
                game_data = app_data.get('data', {})
                
                # 무료 게임 체크
                if game_data.get('is_free', False):
                    return {
                        'price': 0,
                        'currency': 'KRW',
                        'formatted': '무료',
                        'discounted': False,
                        'original_price': 0,
                        'name': game_data.get('name', '알 수 없는 게임')
                    }
                
                # 가격 정보 추출
                price_overview = game_data.get('price_overview', {})
                if price_overview:
                    final_price = price_overview.get('final', 0)
                    initial_price = price_overview.get('initial', final_price)
                    discount_percent = price_overview.get('discount_percent', 0)
                    
                    return {
                        'price': final_price / 100,  # cents to won
                        'currency': price_overview.get('currency', 'KRW'),
                        'formatted': price_overview.get('final_formatted', f'{final_price // 100:,}원'),
                        'discounted': discount_percent > 0,
                        'original_price': initial_price / 100,
                        'discount_percent': discount_percent,
                        'name': game_data.get('name', '알 수 없는 게임')
                    }
                
                # 가격 정보가 없는 경우 (지역 제한 등)
                if 'name' in game_data:
                    return {
                        'price': None,
                        'currency': 'KRW',
                        'formatted': '가격 정보 없음 (지역 제한일 수 있음)',
                        'discounted': False,
                        'original_price': None,
                        'name': game_data.get('name', '알 수 없는 게임')
                    }
                    
        except Exception as e:
            st.warning(f"Steam 가격 조회 중 오류: {str(e)}")
        return None
    
    def get_game_price_info(self, game_name):
        """게임 이름으로 가격 정보 조회"""
        app_id = self.get_steam_app_id(game_name)
        if app_id:
            price_info = self.get_steam_price(app_id)
            if price_info:
                price_info['platform'] = 'Steam'
                price_info['store_url'] = f"https://store.steampowered.com/app/{app_id}/"
                return price_info
        return None