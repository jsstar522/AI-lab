# Youtube comments

## Youtube Crawler

Crawler 폴더는 `Selenium`을 이용해서 댓글을 모았습니다. **스크롤 위치에 따라** 페이지가 동적으로 늘어나기 때문에 스크롤을 끝까지 밑으로 내린 뒤, **댓글 더보기 클릭**, 이후에 모든 댓글들을 긁어옵니다.

## Youtube API

Youtube 화면상 댓글이 작성된 정확한 날짜를 알 수 없어 Crawler는 한계가 많습니다. 더 많은 정보를 제공하는 youtube API를 사용해서 댓글을 추출합니다. 자세한 사용법은 https://developers.google.com/youtube/v3/docs/comments을 참조하세요.