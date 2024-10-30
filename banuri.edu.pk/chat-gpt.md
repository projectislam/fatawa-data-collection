Write a python script which scrap data from a website. Here can some steps you can follow to scrap website data.

Getting total pages

1. Go to this link `https://www.banuri.edu.pk/new-questions`
2. Get last link from pagination for this selector is `body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div:nth-child(3) > nav > ul > li:nth-child(6)` instead of `nth-child(6)` you can use `nth-last` or something, because it is the last `li` in this `ul`
3. `href` link look like this `https://www.banuri.edu.pk/new-questions/page/1242` the last part of this link is total number of pages in this case it is "1242"

Go to each page

1. Go to each page link is `https://www.banuri.edu.pk/new-questions/page/{page_number}`
2. On each page this is `ul` list of questions, selector for this `ul` is `body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div:nth-child(2) > ul`
3. Inside this `ul` each `li` item has `a` extract the url (href) from this link and go to this link which is question page link

Get detail of each question

1. On question page you have to extract these things "issued_at", "title", "question", "answer", "fatwa_number", "dar_ul_ifta", "kitab", "bab" and "fasal"

question page link look like this `https://www.banuri.edu.pk/readquestion/muqtadee-ka-apnay-imaam-ko-luqmah-daynay-ka-hukum-144604100192/06-10-2024`

"issued_at": last part of the url which is date in this case it is "06-10-2024"

"title": get text from selector `body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div:nth-child(2) > h3`

"question": get text form selector `body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div.col-md-12.sawal-jawab > p:nth-child(3)` below is "container sample html" you can see in this container "question" text is come after `<h3 class="question_heading">سوال</h3>` and before `<h4 class="question_heading">جواب</h4>` heading.

"answer": answer is all the html mostly `p` tags which come right after `<h4 class="question_heading">جواب</h4>` and before `<hr class="big-hr">` as you can see in "container sample html"

"fatwa_number": get number from selector `#fatwa_number`

"dar_ul_ifta": will always "banuri"

"kitab", "bab" and "fasal": after second `<hr class="big-hr">` there are multiple `div` with class `.tag` inside these "tag" class there are `a` if link contains "/questions/kitab" then the text inside this `a` tag is "kitab" title and "kitab id" is the last part of link which is in this case is "salat". If link contains "/questions/bab" then the text inside this `a` tag is "bab" title and last part of link is "id" of "baba" which is in this case is "qiraat". If the link contains "/questions/fasal" then the text inside this `a` tag is "fasal" title and last part of this link is "id" of "fasal" which is in this case is "imam-ko-luqma-dena"

container sample html

```html
<div class="col-md-12 sawal-jawab">
  <h3 class="question_heading">سوال</h3>
  <p></p>
  <p style="text-align:justify;">
    نماز میں قرآن مجید کی تلاوت کے اندر چھوٹی سی غلطی یعنی لحنِ خفی کی غلطی میں
    امام کو لقمہ دینے کا حکم کیا ہے ؟
  </p>
  <p></p>
  <h4 class="question_heading">جواب</h4>
  <p></p>
  <p style="text-align:justify;">
    علم تجوید کے اعتبار سے صفات عارضہ کی غلطی کو لحن خفی &nbsp;کہا جاتا ہے ،
    مثلاً لام یا راء کو باریک و موٹا پڑھنے &nbsp; کی صورتوں یا ادغام ، اظہاراور
    اخفاء کا اپنے اپنے مقام پر اہتمام &nbsp;نہ کرنا وغیرہ لحن خفی کہلاتا ہے ۔
    لحن خفی کی صورت میں امام کو لقمہ دینے کا حکم نہیں ہے ، اس طرح کی اغلاط سے
    نماز فاسد نہیں ہوتی البتہ نماز میں کراہت پیدا ہوتی ہے ۔
  </p>
  <p style="text-align:justify;">
    لہذااگرکوئی امام&nbsp;&nbsp;لحنِ خفی کرتاہو، یعنی جس سے معنی میں فساد نہیں
    آتا،توایسی غلطی میں امام کو لقمہ نہیں دیناچاہیے،البتہ لحنِ خفی کے ساتھ قرآن
    کریم کی تلاوت کرنایہ قرآن کریم کے حسن وزینت کے خلاف ہے،لحنِ خفی کے ساتھ
    تلاوت کرنے والے شخص کو کسی ماہر، مجود کےپاس مشق کرکے اپنی قراءت کودرست
    کرلینا چاہیے۔
  </p>
  <p style="text-align:justify;">فتاویٰ شامی میں ہے:</p>
  <p class="indent" style="text-align:justify;">
    <span class="ar_writing"
      >"ومنها القراءة بالألحان إن غير المعنى وإلا لا إلا في حرف مد ولين إذا فحش
      وإلا لا ،بزازية.</span
    >
  </p>
  <p class="indent" style="text-align:justify;">
    <span class="ar_writing"
      >&nbsp;(قوله بالألحان) أي بالنغمات، وحاصلها كما في الفتح إشباع الحركات
      لمراعاة النغم (قوله إن غير المعنى) كما لو قرأ - {الحمد لله رب العالمين}-
      وأشبع الحركات حتى أتى بواو بعد الدال وبياء بعد اللام والهاء وبألف بعد
      الراء، ومثله قول المبلغ رابنا لك الحامد بألف بعد الراء لأن الراب هو زوج
      الأم كما في الصحاح والقاموس وابن الزوجة يسمى ربيبا.</span
    >
  </p>
  <p class="indent" style="text-align:justify;">
    <span class="ar_writing"
      >(قوله وإلا لا إلخ) أي وإن لم يغير المعنى فلا فساد إلا في حرف مد ولين إن
      فحش فإنه يفسد، وإن لم يغير المعنى، وحروف المد واللين وهي حروف العلة
      الثلاثة الألف والواو والياء إذا كانت ساكنة وقبلها حركة تجانسها، فلو لم
      تجانسها فهي حروف علة ولين لا مد. [تتمة]</span
    >
  </p>
  <p class="indent" style="text-align:justify;">
    <span class="ar_writing"
      >فهم مما ذكره أن القراءة بالألحان إذا لم تغير الكلمة عن وضعها ولم يحصل بها
      تطويل الحروف حتى لا يصير الحرف حرفين، بل مجرد تحسين الصوت وتزيين القراءة
      لا يضر، بل يستحب عندنا في الصلاة وخارجها كذا في التتارخانية."</span
    >
  </p>
  <p class="indent" style="text-align:left;">
    (كتاب الصلاة، باب ما يفسد الصلاة وما يكره فيها، فروع مشى المصلي مستقبل
    القبلة هل تفسد صلاته، ج:1، ص:630، ط:دار الفكر بيروت)
  </p>
  <p style="text-align:justify;">التمہید فی علم التجوید میں ہے :</p>
  <p class="indent" style="text-align:justify;">
    <span class="ar_writing"
      >"وأما ‌اللحن ‌الخفي فهو خلل يطرأ على الألفاظ فيخل بالعرف دون
      المعنى....</span
    ><span class="ar_writing"
      >واللحن الخفي هو مثل تكرير الراءات، وتطنين النونات، وتغليظ اللامات
      وإسمانها وتشريبها الغنة، وإظهار المخفى، وتشديد الملين، وتليين المشدد،
      والوقف بالحركات كوامل....</span
    ><span class="ar_writing"
      >وذلك غير مخل بالمعنى، ولا مقصر باللفظ، وإنما الخلل الداخل على اللفظ فساد
      رونقه وحسنه وطلاوته، من حيث إنه جار مجرى الرتة واللثغة....</span
    ><span class="ar_writing"
      >وهذا الضرب من اللحن، وهو الخفي، لا يعرفه إلا القارئ المتقن، والضابط
      المجود، الذي أخذ عن أفواه الأئمة، ولقن من ألفاظ أفواه العلماء الذين ترتضى
      تلاوتهم ويوثق بعربيتهم، فأعطى كل حرف حقه، ونزله منزلته."</span
    >
  </p>
  <p class="indent" style="text-align:left;">
    (الفصل الثانی فی حد اللحن وحقیقتہ فی العرف والوضع، ص:63، ط:مکتبۃ المعارف،
    الریاض)
  </p>
  <p class="indent" style="text-align:left;">فقط واللہ اعلم</p>
  <p></p>
  <hr class="big-hr" />
  <div class="col-sm-6 col-md-6">
    <p style="color:#73161f" class="question_heading">
      فتوی نمبر : <a id="fatwa_number">144604100192</a>
    </p>
  </div>
  <div class="col-sm-6 col-md-6">
    <p style="color:#73161f">
      دارالافتاء : جامعہ علوم اسلامیہ علامہ محمد یوسف بنوری ٹاؤن
    </p>
  </div>
  <hr class="big-hr" />
  <div class="col-sm-4 col-md-4">
    <div class="tag">
      <a href="https://www.banuri.edu.pk/questions/kitab/salat"
        ><i class="icon-docs-bold"></i> نماز</a
      >
    </div>
  </div>
  <div class="col-sm-4 col-md-4">
    <div class="tag">
      <a href="https://www.banuri.edu.pk/questions/bab/qiraat"
        ><i class="icon-docs-bold"></i> قراءت کا بیان</a
      >
    </div>
  </div>
  <div class="col-sm-4 col-md-4">
    <div class="tag">
      <a href="https://www.banuri.edu.pk/questions/fasal/imam-ko-luqma-dena"
        ><i class="icon-docs-bold"></i> امام کو لقمہ دینا</a
      >
    </div>
  </div>
</div>
```

2. Once you get all the data the create new file for this page in "./data/{page_number}.csv" which contains all the question answers detail in this file.

3. Repeat this for each page question and answers

Also show me the script progress
