# Youtube API (comments extract)

총 3가지의 youtube API를 사용합니다.

* **`commentThreads`** : 게시글 하나의 댓글을 추출합니다. (*Error : 최상위 댓글은 추출되나, 대댓글은 최대 5개만 추출되는 버그가 있음*)
* **`comment`** : commentThreads method의 버그를 
* **`search`** : 특정 단어를 검색하면 동영상이 리스트업 됩니다. order에 따라서 리스트업되는 동영상의 성격을 바꿀 수 있습니다. `최근 날짜`, `높은 관련도`, `제목순서`, `높은 조회수`로 동영상을 정렬합니다. 각각의 동영상 id를 추출할 수 있습니다. 

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

* `videoId`

* `maxResults`

* `pageToken`

* `textFormat`