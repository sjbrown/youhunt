<h1>You Hunt! Web Client</h1>
<h2>Judge interface</h2>
Charactor: ${ c } ${ c._jdict }
<br />
Role : ${ role }
<br />
Sumbission: ${ s } ${ s._jdict }
<%
    m = s.mission_Mission__object
%>
<br />
Mission: ${ m } ${ m._jdict }
<br />

<img src="${ s.photo_url }"
 width="200" height="150"
 />

<hr />
% if role == 'judge':
    Is this a picture of ${ m.human_readable() }
    ?

   <ul>
   <li>
    <form action="${ make_url('api:submission judgement', s.id ) }"
          method="post">
    ${ csrf }
    <ul>
        <li><input id="submit_json" type=text name="submit_json"
             value='{"charactor_id":"${c.id}", "judgement":true}'
             /></li>
        <li>
            Base: ${ s.base_pay['yes'] }, Tip: ${ s.tips['yes'] }
        </li>
        <li><input type="submit" value="Yes ${s.pay_yes}"/>
        </li>
    </ul>
    </form>
   </li>
   <li>
    <form action="${ make_url('api:submission judgement', s.id ) }"
          method="post">
    ${ csrf }
    <ul>
        <li><input id="submit_json" type=text name="submit_json"
             value='{"charactor_id":"${c.id}", "judgement":false}'
             /></li>
        <li>
            Base: ${ s.base_pay['no'] }, Tip: ${ s.tips['no'] }
        </li>
        <li><input type="submit" value="No ${s.pay_no}"/>
        </li>
    </ul>
    </form>
   </li>
   </ul>

% endif
