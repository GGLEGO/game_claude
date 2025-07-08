# expanded_game_database.py
import random

class GameDatabase:
    def __init__(self):
        # 감정별, 장르별, 플레이어 수별로 분류된 게임 데이터베이스
        self.games_by_emotion = {
            "긍정": {
                "경쟁": ["Counter-Strike 2", "Valorant", "League of Legends", "Overwatch 2", "Rocket League", "Apex Legends", "Rainbow Six Siege", "Call of Duty: Modern Warfare II"],
                "액션": ["DOOM Eternal", "Cyberpunk 2077", "Devil May Cry 5", "Sekiro: Shadows Die Twice", "Metal Gear Rising: Revengeance", "Bayonetta 3"],
                "어드벤처": ["Spider-Man Remastered", "Horizon Zero Dawn", "Assassin's Creed Valhalla", "Red Dead Redemption 2", "The Witcher 3: Wild Hunt"],
                "파티": ["Fall Guys", "Gang Beasts", "Human: Fall Flat", "Moving Out", "Overcooked! 2", "Among Us", "Jackbox Party Pack", "Keep Talking and Nobody Explodes"]
            },
            "부정": {
                "힐링": ["Stardew Valley", "Journey", "Spiritfarer", "A Short Hike", "ABZÛ", "Gris", "Unpacking"],
                "창조": ["Minecraft", "Terraria", "Cities: Skylines", "Planet Coaster", "The Sims 4", "Two Point Hospital", "House Flipper"],
                "퍼즐": ["Portal 2", "The Witness", "Baba Is You", "Tetris Effect", "Monument Valley", "Return of the Obra Dinn", "Outer Wilds"],
                "이야기": ["Firewatch", "What Remains of Edith Finch", "Life is Strange", "Night in the Woods", "Celeste", "Hades", "Disco Elysium"]
            },
            "중립": {
                "RPG": ["ELDEN RING", "Baldur's Gate 3", "Divinity: Original Sin 2", "Persona 5 Royal", "Final Fantasy XIV", "The Elder Scrolls V: Skyrim", "Mass Effect Legendary Edition"],
                "전략": ["Civilization VI", "Age of Empires IV", "Total War: Warhammer III", "StarCraft II", "Chess.com", "Europa Universalis IV"],
                "시뮬레이션": ["Microsoft Flight Simulator", "Euro Truck Simulator 2", "PowerWash Simulator", "Farming Simulator 22", "Car Mechanic Simulator 2021"],
                "인디": ["Hollow Knight", "Cuphead", "Dead Cells", "Ori and the Will of the Wisps", "Katana ZERO", "Pizza Tower", "Shovel Knight"]
            }
        }
        
        # 플레이어 수별 게임 분류
        self.games_by_players = {
            1: ["Cyberpunk 2077", "The Witcher 3: Wild Hunt", "ELDEN RING", "Hollow Knight", "Stardew Valley", "Portal 2", "Celeste", "Hades", "Journey", "Sekiro: Shadows Die Twice"],
            2: ["It Takes Two", "Portal 2", "Stardew Valley", "Overcooked! 2", "A Way Out", "Unravel Two", "Human: Fall Flat", "Cuphead", "Terraria"],
            3: ["Among Us", "Fall Guys", "Overcooked! 2", "Gang Beasts", "Moving Out", "Terraria", "Minecraft", "Rocket League"],
            4: ["Among Us", "Fall Guys", "Overcooked! 2", "Gang Beasts", "Moving Out", "Jackbox Party Pack", "Minecraft", "Left 4 Dead 2", "Deep Rock Galactic"],
            "5+": ["Among Us", "Fall Guys", "Counter-Strike 2", "Valorant", "League of Legends", "Overwatch 2", "Minecraft", "Garry's Mod", "Jackbox Party Pack"]
        }
        
        # 가격대별 게임 분류 (원화 기준 추정) - 무료 게임 대폭 확장
        self.games_by_price = {
            "무료": [
                # 인기 무료 게임들
                "Counter-Strike 2", "Valorant", "League of Legends", "Apex Legends", 
                "Fortnite", "Genshin Impact", "Lost Ark", "Path of Exile",
                "Dota 2", "Team Fortress 2", "Warframe", "Destiny 2",
                "Fall Guys", "Rocket League", "Among Us",  # 이제 무료
                # 무료 인디 게임들
                "Brawlhalla", "Paladins", "Smite", "World of Tanks",
                "War Thunder", "World of Warships", "Heroes & Generals",
                # 무료 MMO
                "Guild Wars 2", "Star Wars: The Old Republic", "Tera",
                "Blade & Soul", "Black Desert Online", "Neverwinter",
                # 무료 배틀로얄
                "Call of Duty: Warzone", "PUBG: BATTLEGROUNDS", "Apex Legends Mobile",
                # 무료 카드/보드 게임
                "Hearthstone", "Yu-Gi-Oh! Master Duel", "Gwent", "Legends of Runeterra",
                # 무료 시뮬레이션
                "War Thunder", "World of Warplanes"
            ],
            "저가": [
                "Stardew Valley", "Terraria", "Cuphead", "Hollow Knight", "Celeste", 
                "Hades", "Dead Cells", "A Hat in Time", "Shovel Knight",
                "Ori and the Blind Forest", "Pizza Tower", "Katana ZERO",
                "Journey", "ABZÛ", "GRIS", "Unpacking"  # Journey는 Steam에서 저가 게임
            ],  # ~20000원
            "중가": [
                "Portal 2", "Overcooked! 2", "It Takes Two", "Dead Cells", 
                "Ori and the Will of the Wisps", "Subnautica", "The Forest",
                "Valheim", "Raft", "Green Hell"
            ],  # 20000-40000원
            "고가": [
                "Cyberpunk 2077", "The Witcher 3: Wild Hunt", "ELDEN RING", 
                "Baldur's Gate 3", "Call of Duty: Modern Warfare II",
                "FIFA 24", "Red Dead Redemption 2", "Grand Theft Auto V"
            ]  # 40000원+
        }
        
        # 장르별 설명
        self.genre_descriptions = {
            "경쟁": "실력을 겨루고 승부욕을 불러일으키는 게임들",
            "액션": "빠른 반응과 아드레날린이 솟구치는 게임들",
            "어드벤처": "새로운 세계를 탐험하는 모험 게임들",
            "파티": "친구들과 함께 즐기는 파티 게임들",
            "힐링": "마음을 편안하게 해주는 치유 게임들",
            "창조": "상상력을 발휘해 무언가를 만드는 게임들",
            "퍼즐": "논리적 사고를 요구하는 퍼즐 게임들",
            "이야기": "감동적인 스토리가 있는 내러티브 게임들",
            "RPG": "캐릭터를 성장시키고 모험하는 롤플레잉 게임들",
            "전략": "깊은 사고와 계획이 필요한 전략 게임들",
            "시뮬레이션": "현실을 모방한 시뮬레이션 게임들",
            "인디": "독창적인 아이디어가 돋보이는 인디 게임들"
        }

    def get_games_by_emotion_and_players(self, emotion, player_count, max_games=10):
        """감정과 플레이어 수에 맞는 게임들 반환"""
        emotion_games = []
        
        # 감정에 맞는 게임들 수집
        if emotion in self.games_by_emotion:
            for genre, games in self.games_by_emotion[emotion].items():
                emotion_games.extend(games)
        
        # 플레이어 수에 맞는 게임들 필터링
        player_suitable_games = []
        
        # 정확한 플레이어 수 매칭
        if player_count in self.games_by_players:
            player_suitable_games.extend(self.games_by_players[player_count])
        
        # 5명 이상인 경우
        if player_count >= 5:
            player_suitable_games.extend(self.games_by_players["5+"])
        
        # 감정과 플레이어 수 모두에 맞는 게임들
        suitable_games = list(set(emotion_games) & set(player_suitable_games))
        
        # 적합한 게임이 부족하면 감정만 고려
        if len(suitable_games) < 3:
            suitable_games.extend([game for game in emotion_games if game not in suitable_games])
        
        # 그래도 부족하면 플레이어 수만 고려
        if len(suitable_games) < 3:
            suitable_games.extend([game for game in player_suitable_games if game not in suitable_games])
        
        # 중복 제거 및 섞기
        suitable_games = list(set(suitable_games))
        random.shuffle(suitable_games)
        
        return suitable_games[:max_games]

    def get_games_by_price_range(self, budget_text):
        """예산에 맞는 가격대의 게임들 반환"""
        if not budget_text:
            return []
        
        # 예산에서 숫자 추출
        import re
        budget_numbers = re.findall(r'[\d,]+', budget_text.replace(',', ''))
        if not budget_numbers:
            return self.games_by_price["저가"]  # 기본값
        
        try:
            budget = int(budget_numbers[0])
            if budget == 0:
                return self.games_by_price["무료"]
            elif budget <= 20000:
                return self.games_by_price["무료"] + self.games_by_price["저가"]
            elif budget <= 40000:
                return self.games_by_price["무료"] + self.games_by_price["저가"] + self.games_by_price["중가"]
            else:
                # 모든 가격대 포함
                all_games = []
                for games in self.games_by_price.values():
                    all_games.extend(games)
                return all_games
        except:
            return self.games_by_price["저가"]

    def get_random_diverse_games(self, count=10):
        """다양한 장르에서 랜덤하게 게임 선택"""
        diverse_games = []
        all_genres = []
        
        # 모든 장르의 게임들 수집
        for emotion_data in self.games_by_emotion.values():
            for genre, games in emotion_data.items():
                all_genres.append((genre, games))
        
        # 각 장르에서 하나씩 선택
        random.shuffle(all_genres)
        for genre, games in all_genres:
            if len(diverse_games) < count:
                game = random.choice(games)
                if game not in diverse_games:
                    diverse_games.append(game)
        
        return diverse_games

    def get_genre_info(self, genre):
        """장르 설명 반환"""
        return self.genre_descriptions.get(genre, "다양한 재미를 제공하는 게임들")

    def get_similar_games(self, game_name, count=5):
        """비슷한 게임들 찾기"""
        similar_games = []
        
        # 해당 게임이 속한 장르들 찾기
        target_genres = []
        for emotion_data in self.games_by_emotion.values():
            for genre, games in emotion_data.items():
                if game_name in games:
                    target_genres.append(genre)
        
        # 같은 장르의 다른 게임들 수집
        for emotion_data in self.games_by_emotion.values():
            for genre, games in emotion_data.items():
                if genre in target_genres:
                    for game in games:
                        if game != game_name and game not in similar_games:
                            similar_games.append(game)
        
        random.shuffle(similar_games)
        return similar_games[:count]