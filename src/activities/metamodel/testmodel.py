# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at>"""
__docformat__ = 'plaintext'

import activities.metamodel as mm

profile = mm.Profile('pr')
#profile['execution1'] = mm.Stereotype()
#profile['execution1']['tgv'] = mm.TaggedValue()

model = mm.Package('testmodel')
model[profile.__name__] = profile
model['main'] = mm.Activity()
act = model['main']

act['pc1'] = mm.PreConstraint(specification='True is True')
act['po1'] = mm.PostConstraint(specification='False is False')

act['start'] = mm.InitialNode()
act['fork'] = mm.ForkNode()

act['action1'] = mm.OpaqueAction()
act['action1']['execution1'] = mm.Stereotype(profile=profile)
act['action1']['execution1']['tgv'] = mm.TaggedValue(value="dummy value")
act['action1']['lpc1'] = mm.PreConstraint(specification='True is True')
act['action1']['lpo1'] = mm.PostConstraint(specification='False is False')

act['action2'] = mm.OpaqueAction()
act['action3'] = mm.OpaqueAction()

act['join'] = mm.JoinNode()
act['decision'] = mm.DecisionNode()
act['merge'] = mm.MergeNode()

act['flow end'] = mm.FlowFinalNode()
act['end'] = mm.ActivityFinalNode()

act['1'] = mm.ActivityEdge(source=act['start'], target=act['fork'])
act['2'] = mm.ActivityEdge(source=act['fork'], target=act['action1'])
act['3'] = mm.ActivityEdge(source=act['fork'], target=act['action2'])
act['4'] = mm.ActivityEdge(source=act['action1'], target=act['action3'])
act['5'] = mm.ActivityEdge(source=act['action2'], target=act['join'])
act['6'] = mm.ActivityEdge(source=act['action3'], target=act['decision'])
act['7'] = mm.ActivityEdge(source=act['action3'], target=act['join'])
act['8'] = mm.ActivityEdge(source=act['decision'], target=act['flow end'], guard="else")
act['9'] = mm.ActivityEdge(source=act['decision'], target=act['merge'], guard="True")
act['10'] = mm.ActivityEdge(source=act['join'], target=act['merge'])
act['11'] = mm.ActivityEdge(source=act['merge'], target=act['end'])

mm.validate(model)
#