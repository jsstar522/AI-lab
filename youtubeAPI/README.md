# Youtube API (comments extract)

총 3가지의 youtube API를 사용합니다.

* **`commentThreads`** : **하나의 videoID를 인자로 받아와서 댓글을 추출합니다.** (*Error : 최상위 댓글은 추출되나, 대댓글은 최대 5개만 추출되는 버그가 있음*)
* **`comment`** : **하나의 commentID를 인자로 받아와서 댓글의 정보와 댓글에 달린 대댓글을 추출합니다.** commentThreads API의 버그(대댓글이 최대 5개까지 밖에 추출되지 않음)를 보완합니다. 
* **`search`** : **search term(검색어)와 옵션을 인자로 받아와서 videoID를 추출합니다.** order에 따라서 리스트업되는 동영상의 성격을 바꿀 수 있습니다. `최근 날짜`, `높은 관련도`, `제목순서`, `높은 조회수`로 동영상을 정렬합니다.  

`commentThreads`와 `comment` API는 작동방식이 같으므로 `commentAPI.py` 파일에 통합시켰습니다.

`search` API는 `searchAPI.py`에서 사용하고 `commentAPI.py`에서 모듈로 사용됩니다.

## Google Development API

Google API를 사용하기 위해서 사용자인증과 토큰 발급이 필요합니다. 사용자 인증은  https://console.developers.google.com/apis에서 진행합니다.

1. 사이트에 접속 후 새로운 프로젝트를 생성합니다. 원하는 이름으로 프로젝트를 생성하세요.![credential_1](img/credential_1.png)
2. 프로젝트가 생성되면 왼쪽 메뉴, `API 및 서비스`에서 `라이브러리`를 누르고 검색창에 "Youtube"라고 칩니다. 우리는 Youtube Data API v3를 사용할 것입니다. Youtube Data API v3를 눌러 `사용설정`을 누릅니다. ![credential_2](img/credential_2.png)
3. API를 사용할 때, 사용자의 동의를 받는 내용을 설정합니다. 특별히 **개인 서버에서 다른 사용자에게 배포할 용도가 아니므로 사용자 인증정보 - 상단메뉴, `OAuth 동의화면`에서 어플리케이션 이름만 넣고 저장합니다.**
4. 이제 youtubeAPI를 사용할 사용자를 인증하는 절차를 밟겠습니다. 사용자 인증은 두갈레로 나뉩니다. 
   * `commentAPI`를 사용하기 위해서는 사용자가 누구인지(로그인 정보), 어디서 사용할 건지(서버, 클라이언트…) 등의 내용이 필요하기 때문에 이러한 내용을 포함한 토큰을 발급받는 `OAuth 2.0`으로 사용자를 인증합니다. (이는 댓글을 달거나 비디오를 올리는 자동화 된 API를 포함하고 있으므로 로그인 정보가 필요하기 때문입니다.)
   * `searchAPI`는 사용자 정보는 필요하지 않기 때문에 간단하게 `API Key`만 발급받으면 됩니다.

### OAuth 2.0

1. 다시 홈으로 돌아가, 왼쪽 메뉴에서 `사용자 인증 정보`를 클릭합니다. 사용자 인증 정보를 아직 만들지 않았으므로 `사용자 인증 정보 만들기` 버튼이 활성화 되어있습니다. 버튼을 누른 뒤 `OAuth 클라이언트 ID`를 누릅니다. ![credential_3](img/credential_3.png)
2. **어플리케이션 유형**은 `웹 어플리케이션`을 선택하고 이름을 입력합니다.
3. 로컬에서만 사용하므로 **승인된 자바스크립트 원본**은 `http://localhost`를 입력합니다.
4. `리디렉션 URI`는 사용자가 동의버튼을 누르면 이동하는 경로입니다. `http://localhost/oauth2callback`과 `http://localhost:8080/`을 추가합니다. ![credential_4](img/credential_4.png)
5. 생성을 누릅니다.

이제 내 정보를 포함한 `client_secrets`이 생겼습니다. 생성된 사용자 인증의 오른쪽에 `다운로드 버튼`을 클릭해서 JSON파일을 다운로드 받을 수 있습니다. `client_secrets`으로 이름을 변경한 뒤, 이 프로젝트 폴더에 넣습니다. ![credential_5](img/credential_5.png)

### API Key

1. 이번에는 API Key를 만들겠습니다. `사용자 인증 정보 만들기`를 클릭한 뒤, `API 키`를 누릅니다.
2. 끝입니다. API Key가 생성됐습니다. 이 값은 나중에 `searchAPI.py` 파일 안에서 사용됩니다.



## AWS DB 설정

*https://github.com/pseudotop/crawler-news 을 참고하고 AWS db에 관련된 모듈은 모두 여기에 있는 내용을 조금만 변형했습니다.*



## Youtube API commentThreads

*https://developers.google.com/youtube/v3/docs/commentThreads/list을 참고했습니다.*

Youtube API가 제공하는 수많은 메서드 중에서 댓글을 추출할 수 있는 `commentThreads.list`를 사용했습니다. **이 메서드는 `필수 인자(required)`, `필터링 인자(filters)`, `옵션 인자(option)`의 종류인 수많은 parameter를 받습니다.** 많은 parameter 중에서 다음과 같은 parameter만 사용했습니다.

* `part` : commentThreads.list 메서드는 `,`로 나뉘어진 배열의 결과를 반환합니다. 배열안에 있는 데이터는 key-value 형식으로 구성되는데,  `snippet(최상위 댓글)`의 key를 가진 value와 `replies(대댓글)`의 key를 가진 value를 각각 반환시킬 수 있습니다. 하나의 게시글에 달린 댓글은 다음과 같은 구조를 갖습니다.

  ```text
  item
  ├── snippet
  │   ├── textDisplay (최상위 댓글1)
  │   ├── replies
  │   |	├── snippet
  |	|	|	├── textDisplay (댓글1의 대댓글1)
  │   |	├── snippet
  |	|	|	├── textDisplay (댓글1의 대댓글2)
  ├── snippet
  │   ├── textDisplay (최상위 댓글2)
  .
  .
  .
  ```

* `videoId` : 해당 videoID를 가진 비디오의 댓글 item을 가져옵니다.

* `maxResults` : 

* `pageToken` : 

* `textFormat` :











### 필요한 라이브러리

httplib2

apiclient

apiclient.discovery - `sudo pip3 install --upgrade google-api-python-client`으로 설치
oauth2client

googleapiclient - `pip3 install --upgrade google-api-python-client --user`으로 설치