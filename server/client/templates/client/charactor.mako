<h1>You Hunt! Web Client</h1>
<h2>Logged-in player charactor interface</h2>
Charactor: ${ c }
<br />
Activity: ${ c.activity }
<br />
Potential missions: ${ c.potential_missions }
<h3>Game ${ g.id } ${ g } Started? ${ g.started }
</h3>
<ul>
        <li>Charactors ${ [str(x) for x in g.charactor_set.all()] }</li>

        % if not g.started:
            <li>Current invites ${ g.invites }
            <li>Invite players to game ${ g }
            % if start_allowed:
                <li><a href="${ make_url('api:game start', g.id) }"
                >Start game ${ g }</a>
            % endif
        % else:
            <li>
            % if c.activity == 'choosing_mission':
                <%include file='activity_choosing_mission.mako' />
            % endif
            % if c.activity == 'hunting':
                <%include file='activity_hunting.mako' />
            % endif
        % endif
</ul>


