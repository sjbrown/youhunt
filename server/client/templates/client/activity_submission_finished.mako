<div
 style="background:#f0f0f0"
 ><h3>Submission Finished</h3>

${ c.id } ${ c }, your mission, ${ c.human_readable_mission() },
<%
    s = c.submission
    judge = c.submission.winning_judge_Charactor__object
%>

<b>
% if s.judgement == True:
    Succeeded!
% else:
    Failed!
% endif
</b>
<br />
This judgement was handed down by <b>${judge}</b>
<br />


Photo
<img src="${ s.photo_url }"
 width="200" height="150"
  />
<br />
Submission ${ s } ${ s._jdict }
<br />
<ul>
% if s.judgement == True:
    <li>
    You were awarded $$$
    </li>
% else:
    <li>
    Bounty against <b>${judge}</b> creation goes here
    </li>
% endif

<li>
<form action="${ make_url('api:submission dismissal', s.id) }"
      method="post">
${ csrf }
<ul>
    <li><input id="dismiss_json" type=text name="dismiss_json"
         value='{"charactor_id":"${c.id}"}'
         /></li>
    <li><input type="submit" value="Dismiss" />
    </li>
</ul>

</form>
</li>
</ul>

</div>
