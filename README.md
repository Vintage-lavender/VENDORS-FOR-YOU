# 📦 Vendors-for-You
> 거리·평점·배달비·조리시간 기준으로 정렬해 주는 데스크톱 GUI 애플리케이션

## 목적
- **내 주변 가게를 거리·평점·배달비·조리시간 기준으로 한눈에 비교**
- **MySQL** 로컬 데이터베이스와 간단한 Python GUI(Tkinter)로 기능 구현

## 프로젝트 진행 기한
- 2023.10.30 ~ 2023.12.04
  
## 주요 기능
| 기능 | 설명 |
|-----|-----|
| 위치 기반 정렬 | 선택한 위치에서 가게까지의 **거리 순** 정렬 |
| 커스텀 정렬 | **평점·배달비·조리시간** 버튼으로 즉시 재정렬 |
| 영업 중 필터 | **OPEN** 버튼으로 현재 영업 중인 가게만 보기 |
| 좋아요 관리 | 가게를 ♥ ‘좋아요’로 저장 & **View Likes** 로 한 번에 확인 |
| 상세 정보 | **Show Details** 버튼으로 배달비, 운영시간 등 추가 정보 표시 |

## 스크린샷
| 초기 화면 예시 |
|---|
| <img width="415" alt="Vendors-for-You demo" src="https://github.com/Vintage-lavender/VENDORS-FOR-YOU/assets/96819499/6bd3870e-0ca7-48d1-8f12-30143d1afe6e"> |

## 빠른 시작

### 1) 레포 클론
```bash
git clone https://github.com/Vintage-lavender/VENDORS-FOR-YOU.git
cd VENDORS-FOR-YOU
```
### 2) 데이터베이스 생성 및 초기 데이터 삽입
```bash
mysql -u root -p < group5-db-dump.sql
```
- 단, 기존에 project라는 이름의 DB가 있었다면, 기존 DB를 백업해두고 실행
  ```bash
  mysqldump -u root -p project > project-backup.sql
  ```

### 3) 패키지 설치
```bash
pip install -r requirements.txt
```
### 4) GUI 실행
```bash
python GUI/group5-main.py
```

## 사용 방법

### 1. 로그인
- 예시 ID  
  - `IL9MJSW`  
  - `00OT8JX`  
  - `30PZXDS`

### 2. 위치 및 카테고리 선택
- 로그인 후, **위치**를 선택합니다.
- `Major Category` → `Sub Category` 를 차례로 선택하여 메뉴를 찾습니다.

### 3. 가게 목록 살펴보기
- 목록은 기본적으로 **거리 순**으로 정렬됩니다.
- 상단 버튼으로 즉시 재정렬  
  - `평점` · `배달비` · `조리시간`
- **OPEN** 버튼을 누르면 현재 영업 중인 가게만 필터링됩니다.

### 4. 좋아요(♥) 관리
- 가게 카드를 클릭해 ♥ ‘좋아요’ 표시
- **View Likes** 버튼으로 내가 좋아요를 누른 가게만 빠르게 확인 가능합니다.

### 5. 상세 정보 확인
- 각 가게 카드에서 **Show Details** 를 클릭하면  
  주소, 전화번호, 운영시간 등 추가 정보를 볼 수 있습니다.

## 주요 기여
- 프로젝트의 일정을 계획하고, 데이터 전처리, 프로토타입 제작 및 코드 구현, 코드 수합 및 정리 등의 프로젝트 전반의 작업들을 수행했습니다.
- 좋아요 관리를 위한 기능들을 구현했습니다.
