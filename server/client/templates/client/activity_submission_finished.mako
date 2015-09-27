<div
 style="background:#f0f0f0"
 ><h3>Submission Finished</h3>

<%
    s = c.submission
    m = s.mission_Mission__object
    judge = c.submission.winning_judge_Charactor__object
    prey = s.stakeholders['prey']
%>
${ c.id } ${ c }, your mission, ${ m.human_readable() },

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
    Bounty against Judge <b>${judge}</b>
    <form action="${ make_url('api:new bounty') }"
          method="post">
    ${ csrf }
    <ul>
        <li><input id="bounty_json" type=text name="bounty_json"
             value='{"poster_id":"${c.id}", "target_id":"${judge.id}", "amount":50}'
             /></li>
        <li><input type="submit" value="New Bounty" />
        </li>
    </ul>
    </form>
    </li>
    <li>
    Bounty against Prey <b>${prey}</b>
    <form action="${ make_url('api:new bounty') }"
          method="post">
    ${ csrf }
    <ul>
        <li><input id="bounty_json" type=text name="bounty_json"
             value='{"poster_id":"${c.id}", "target_id":"${prey.id}", "amount":50}'
             /></li>
        <li><input type="submit" value="New Bounty" />
        </li>
    </ul>
    </form>
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
