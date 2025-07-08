# game_utils.py
import re

def clean_extracted_game_name(raw_name):
    """추출된 게임 이름 정리"""
    if not raw_name:
        return None
        
    # 앞뒤 공백 및 특수문자 제거
    clean_name = raw_name.strip().strip('":\'.,!?()[]{}')
    
    # 불필요한 텍스트 제거
    clean_name = re.sub(r'^(?:게임명?:?\s*)', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'^(?:추천:?\s*)', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'^\d+\.\s*', '', clean_name)  # 숫자. 제거
    
    # 너무 길거나 짧은 이름 필터링
    if len(clean_name) < 2 or len(clean_name) > 50:
        return None
        
    # 일반적이지 않은 문자가 포함된 경우 필터링
    if re.search(r'[^\w\s\-:\'\"&\.]', clean_name):
        return None
        
    return clean_name

def extract_game_names_from_response(response_text):
    """Claude 응답에서 게임 이름 추출 (개선된 버전)"""
    # 다양한 패턴으로 게임 이름 찾기
    patterns = [
        r'\*\*(.*?)\*\*',  # **게임명**
        r'#{1,3}\s*(.*?)(?:\n|$)',  # # 게임명
        r'(?:게임명?:?\s*[\"`\']?)([\w\s:\'\"&\-\.]+?)(?:[\"`\']?(?:\n|,|\.|$))',  # 게임명: 형태
        r'(?:추천[:：]\s*)([\w\s:\'\"&\-\.]+?)(?:\n|,|\.|$)',  # 추천: 게임명
        r'(?:^|\n)\d+\.\s*([\w\s:\'\"&\-\.]+?)(?:\n|,|\.|$)',  # 1. 게임명
    ]
    
    games = []
    seen_games = set()
    
    # 먼저 강조된 게임명들 찾기
    for pattern in patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            clean_name = clean_extracted_game_name(match)
            if clean_name and clean_name.lower() not in seen_games and len(clean_name) > 2:
                games.append(clean_name)
                seen_games.add(clean_name.lower())
                if len(games) >= 3:  # 3개로 제한
                    break
        if len(games) >= 3:
            break
    
    # 잘 알려진 게임들 직접 찾기 (대폭 확장됨)
    if len(games) < 3:
        known_games = [
            # 인기 멀티플레이어 게임들
            'Counter-Strike 2', 'VALORANT', 'League of Legends', 'Overwatch 2', 'Apex Legends',
            'Rocket League', 'Among Us', 'Fall Guys', 'Fortnite', 'Minecraft',
            
            # 협동 게임들
            'It Takes Two', 'Overcooked! 2', 'Portal 2', 'Left 4 Dead 2', 'Deep Rock Galactic',
            'A Way Out', 'Human: Fall Flat', 'Gang Beasts', 'Moving Out', 'Terraria',
            
            # 싱글플레이어 명작들
            'The Witcher 3: Wild Hunt', 'Cyberpunk 2077', 'ELDEN RING', 'Hades', 'Celeste',
            'Hollow Knight', 'Stardew Valley', 'Journey', 'Portal 2', 'Disco Elysium',
            
            # RPG 게임들
            "Baldur's Gate 3", 'Divinity: Original Sin 2', 'Persona 5 Royal', 
            'The Elder Scrolls V: Skyrim', 'Mass Effect Legendary Edition', 'Final Fantasy XIV',
            
            # 액션 게임들
            'Devil May Cry 5', 'Sekiro: Shadows Die Twice', 'DOOM Eternal', 'Cuphead',
            'Dead Cells', 'KATANA ZERO', 'Metal Gear Rising: Revengeance',
            
            # 전략/시뮬레이션 게임들
            "Sid Meier's Civilization VI", 'Age of Empires IV', 'Cities: Skylines',
            'Total War: WARHAMMER III', 'Microsoft Flight Simulator', 'The Sims 4',
            
            # 인디/아트 게임들
            'Ori and the Will of the Wisps', 'GRIS', 'ABZÛ', 'Unpacking', 'A Short Hike',
            'What Remains of Edith Finch', 'Firewatch', 'The Witness', 'Outer Wilds',
            
            # 파티 게임들
            'Jackbox Party Pack', 'Keep Talking and Nobody Explodes', 'Overcooked! All You Can Eat',
            
            # 힐링 게임들
            'Spiritfarer®: Farewell Edition', 'Animal Crossing: New Horizons', 'PowerWash Simulator',
            
            # 경쟁 게임들
            "Tom Clancy's Rainbow Six Siege", 'Call of Duty: Modern Warfare II', 'StarCraft II'
        ]
        
        response_lower = response_text.lower()
        for known_game in known_games:
            known_game_lower = known_game.lower()
            # 정확한 매칭 또는 부분 매칭 확인
            if (known_game_lower in response_lower or 
                any(word in response_lower for word in known_game_lower.split() if len(word) > 3)):
                if known_game not in games:
                    games.append(known_game)
                    if len(games) >= 3:
                        break
    
    return games[:3]  # 정확히 3개만 반환

def format_price_display(price_info, game_name):
    """가격 정보를 보기 좋게 포맷팅 (게임명 포함)"""
    if not price_info:
        return f"🔍 **{game_name}** - Steam에서 확인 불가 (다른 플랫폼에서 무료/유료로 이용 가능할 수 있음)"
    
    if price_info['price'] == 0:
        display = f"🆓 **{game_name}** - 무료"
    else:
        display = f"💰 **{game_name}** - {price_info['formatted']}"
        
        if price_info.get('discounted', False):
            discount = price_info.get('discount_percent', 0)
            original = price_info.get('original_price', 0)
            display += f" ~~{original:,.0f}원~~ (-{discount}% 할인!)"
    
    # Steam에서 가격 정보를 찾은 경우에만 링크 제공
    if price_info.get('store_url'):
        display += f" | [Steam에서 구매하기]({price_info['store_url']})"
    
    return display

def check_price_within_budget(price_info, budget_text):
    """예산 범위 내인지 확인 (개선됨)"""
    if not price_info or not budget_text:
        return True  # Steam에서 찾을 수 없는 게임은 무료일 가능성이 높으므로 예산 내로 간주
    
    # 가격 정보가 없는 경우 (지역 제한 등)
    if price_info.get('price') is None:
        return True
    
    # 무료 게임은 항상 예산 내
    if price_info.get('price', 0) == 0:
        return True
    
    # 예산에서 숫자 추출 (더 정확한 파싱)
    import re
    
    # "무료", "공짜" 등의 키워드 체크
    if any(word in budget_text.lower() for word in ['무료', '공짜', '0원', '돈 없']):
        return price_info.get('price', 0) == 0
    
    # "상관없", "무제한" 등의 키워드 체크
    if any(word in budget_text.lower() for word in ['상관없', '무제한', '얼마든지', '많이']):
        return True
    
    # 숫자 추출 (콤마, 원, 만원 등 처리)
    budget_numbers = re.findall(r'[\d,]+', budget_text.replace(',', ''))
    if not budget_numbers:
        return True  # 예산을 파싱할 수 없으면 OK로 간주
    
    try:
        budget_str = budget_numbers[0]
        budget = int(budget_str)
        
        # "만원" 처리
        if '만' in budget_text:
            budget *= 10000
        
        game_price = price_info['price']
        return game_price <= budget
        
    except (ValueError, TypeError):
        return True  # 파싱 실패 시 OK로 간주