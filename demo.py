# demo_app.py - 다양한 사이드바 사용 예시
import streamlit as st
from sidebar import (
    render_conversation_sidebar,
    render_standard_sidebar, 
    render_analytics_sidebar,
    render_help_sidebar,
    render_custom_sidebar,
    add_sidebar_metric,
    add_sidebar_chart
)

def main():
    st.title("🎮 사이드바 컴포넌트 데모")
    
    # 사이드바 타입 선택
    sidebar_type = st.selectbox(
        "사이드바 타입을 선택하세요:",
        ["대화형", "일반형", "분석형", "도움말", "커스텀"]
    )
    
    if sidebar_type == "대화형":
        st.write("## 💬 대화형 사이드바")
        st.write("대화 진행 상황과 수집된 정보를 표시합니다.")
        
        # 예시 데이터
        current_step = st.selectbox("현재 단계:", ["greeting", "feeling", "players", "budget", "recommendation"])
        user_data = {
            "name": "김민수",
            "emotion": "긍정",
            "player_count": 2,
            "budget": "2만원"
        }
        
        render_conversation_sidebar(current_step, user_data)
    
    elif sidebar_type == "일반형":
        st.write("## 📊 일반형 사이드바")
        st.write("시스템 정보와 게임 데이터베이스 기능을 제공합니다.")
        
        # 게임 데이터베이스 없이 렌더링
        render_standard_sidebar()
    
    elif sidebar_type == "분석형":
        st.write("## 📈 분석형 사이드바")
        st.write("통계 정보와 설정을 표시합니다.")
        
        # 예시 통계 데이터 설정
        if "recommendation_stats" not in st.session_state:
            st.session_state.recommendation_stats = {
                "total_recommendations": 127,
                "today_recommendations": 8,
                "popular_genres": {
                    "액션": 45,
                    "RPG": 32,
                    "힐링": 28,
                    "파티": 22
                }
            }
        
        render_analytics_sidebar()
    
    elif sidebar_type == "도움말":
        st.write("## ❓ 도움말 사이드바")
        st.write("사용법과 문제 해결 정보를 제공합니다.")
        
        render_help_sidebar()
    
    elif sidebar_type == "커스텀":
        st.write("## 🛠️ 커스텀 사이드바")
        st.write("사용자 정의 사이드바를 만들 수 있습니다.")
        
        def custom_content(**kwargs):
            st.write("### 🎯 맞춤 기능")
            
            # 메트릭 추가
            col1, col2 = st.columns(2)
            with col1:
                st.metric("플레이 시간", "2.5시간")
            with col2:
                st.metric("추천 점수", "98%")
            
            # 차트 데이터
            import pandas as pd
            chart_data = pd.DataFrame({
                '일': ['월', '화', '수', '목', '금'],
                '게임시간': [2, 3, 1, 4, 2.5]
            }).set_index('일')
            
            st.write("### 📊 주간 게임 시간")
            st.line_chart(chart_data)
            
            # 설정
            st.write("### ⚙️ 설정")
            auto_recommend = st.checkbox("자동 추천", True)
            difficulty = st.slider("난이도", 1, 5, 3)
            
            if st.button("🎮 새 게임 찾기"):
                st.balloons()
        
        render_custom_sidebar("🎮 게임 대시보드", custom_content)
    
    # 메인 콘텐츠
    st.write("---")
    st.write("### 📝 메인 콘텐츠 영역")
    st.write("여기에 주요 앱 콘텐츠가 표시됩니다.")
    
    # 사이드바 유틸리티 함수 데모
    if st.button("📊 사이드바에 메트릭 추가"):
        add_sidebar_metric("새 메트릭", "42", "↗️ +5")
    
    if st.button("📈 사이드바에 차트 추가"):
        import pandas as pd
        chart_data = pd.DataFrame({
            'values': [1, 3, 2, 4, 3, 5, 4]
        })
        add_sidebar_chart(chart_data, "area")

if __name__ == "__main__":
    main()