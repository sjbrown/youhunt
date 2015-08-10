<div
 style="background:#f0f0f0"
 ><h3>Choosing mission</h3>

${ c.id } ${ c }, your mission is to get a photo of:
<br />
<select>
% for prey in c.potential_prey_Charactor__objects:
    <option>${ prey |h} (${ prey.id })</option>
% endfor
</select>
Doing stunt:
<%
    stunt = c.choose_stunt()
%>
${ stunt }
<br />
<a href="${ make_url('client:charactor', c.id) }">I want a different mission</a>
<br />
I accept this mission:
<form action="${ make_url('api:charactor accept', c.id) }" method="post">
${ csrf }
<ul>
    <li><input id="accept_json" type=text name="accept_json"
         value='{"prey":"5", "stunt":"${stunt.id}"}'
         /></li>
    <li><input type="submit" />
    </li>
</ul>


</form>

</div>
