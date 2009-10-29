# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at>"""
__docformat__ = 'plaintext'

from zodict.node import Node
from zope.interface import implements
from activities.metamodel.interfaces import ActivitiesException
from activities.metamodel.interfaces import IElement

from activities.metamodel.interfaces import IAction
from activities.metamodel.interfaces import IActivity
from activities.metamodel.interfaces import IActivityEdge
from activities.metamodel.interfaces import IActivityFinalNode
from activities.metamodel.interfaces import IActivityNode
from activities.metamodel.interfaces import IBehavior
from activities.metamodel.interfaces import IConstraint
from activities.metamodel.interfaces import IControlNode
from activities.metamodel.interfaces import IDecisionNode
from activities.metamodel.interfaces import IFinalNode
from activities.metamodel.interfaces import IFlowFinalNode
from activities.metamodel.interfaces import IForkNode
from activities.metamodel.interfaces import IInitialNode
from activities.metamodel.interfaces import IJoinNode
from activities.metamodel.interfaces import IMergeNode
from activities.metamodel.interfaces import IOpaqueAction
from activities.metamodel.interfaces import IPreConstraint
from activities.metamodel.interfaces import IPostConstraint

from activities.metamodel.interfaces import IPackage
from activities.metamodel.interfaces import IProfile
from activities.metamodel.interfaces import IStereotype
from activities.metamodel.interfaces import ITaggedValue

#from persistent import Persistent

### HELPER CLASSES
class ModelIllFormedException(ActivitiesException):
    pass


### ABSTRACT BASE CLASSES
# class Element(Persistent):
class Element(Node):
    # TODO: make superclass (Persistent or not...) of element provided by an
    # Interface factory to inject this dependency from outside.
    implements(IElement)
    abstract = True
    xmiid = None

    def check_model_constraints(self):
        try:
            assert(not self.abstract)
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "Cannot directly use abstract base classes"

    @property
    def stereotypes(self):
        return [o for o in self.filtereditems(IStereotype)]


class ActivityNode(Element):
    implements(IActivityNode)
    abstract = True

    def check_model_constraints(self):
        super(ActivityNode, self).check_model_constraints()
        try:
            assert self.__parent__ is not None
            assert IActivity.providedBy(self.__parent__)
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "An ActivityNode must have an Activity as parent"

    @property
    def activity(self):
        return self.__parent__

    # cache this
    @property
    def incoming_edges(self):
        return [obj for obj in self.activity.filtereditems(IActivityEdge)\
                if obj.target.uuid == self.uuid]

    # cache this
    @property
    def outgoing_edges(self):
        return [obj for obj in self.activity.filtereditems(IActivityEdge)\
                if obj.source.uuid == self.uuid]


class Action(ActivityNode):
    implements(IAction)
    abstract = True

    # TODO: leave or remove?
    @property
    def context(self):
        return self.activity.context

    @property
    def preconditions(self):
        return [obj for obj in self.filtereditems(IPreConstraint)]

    @property
    def postconditions(self):
        return [obj for obj in self.filtereditems(IPostConstraint)]


class Behavior(Element):
    implements(IBehavior)
    abstract = True

    def __init__(self, name=None, context=None):
        self.context = context
        super(Behavior, self).__init__(name)

    @property
    def preconditions(self):
        return [o for o in self.filtereditems(IPreConstraint)]

    @property
    def postconditions(self):
        return [o for o in self.filtereditems(IPostConstraint)]


class ControlNode(ActivityNode):
    implements(IControlNode)
    abstract = True

class FinalNode(ControlNode):
    implements(IFinalNode)
    abstract = True

    def check_model_constraints(self):
        super(FinalNode, self).check_model_constraints()
        try:
            assert super(FinalNode, self).outgoing_edges == []
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  u"FinalNode cannot have outgoing edges"

### CONCRETE CLASSES
class Package(Element):
    implements(IPackage)
    abstract = False

    @property
    def profiles(self):
        return [o for o in self.filtereditems(IProfile)]

    @property
    def activities(self):
        return [o for o in self.filtereditems(IActivity)]

class Activity(Behavior):
    implements(IActivity)
    abstract = False

    def check_model_constraints(self):
        super(Activity, self).check_model_constraints()
        try:
            assert(IPackage.providedBy(self.package))
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "An activity must have exactly one package as parent."

    @property
    def package(self):
        return self.__parent__

    @property
    def nodes(self):
        return [o for o in self.filtereditems(IActivityNode)]

    @property
    def edges(self):
        return [o for o in self.filtereditems(IActivityEdge)]

    # Convinience method, not defined by UML 2.2 specification
    @property
    def actions(self):
        return [o for o in self.filtereditems(IAction)]


class OpaqueAction(Action):
    implements(IOpaqueAction)
    abstract = False


class ActivityEdge(Element):
    implements(IActivityEdge)
    abstract = False

    def check_model_constraints(self):
        super(ActivityEdge, self).check_model_constraints()
        try:
            assert self.source or self.target is not None
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "An ActivityEdge must have source and target set"

        # [1]
        try:
            assert self.source.activity is self.target.activity
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "Source and target must be in the same activity"

        # [2]
        try:
            assert self.__parent__ is not None
            assert IActivity.providedBy(self.__parent__)
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "An ActivityEdge must have an Activity as parent"

        try:
            assert IActivityNode.providedBy(self.source)
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "An ActivityEdge must have an ActivityNode as source"

        try:
            assert IActivityNode.providedBy(self.target)
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "An ActivityEdge must have an ActivityNode as target"

    source_uuid = None
    target_uuid = None

    def __init__(self, name=None, source=None, target=None, guard=None):
        # TODO: bool(source) evals to False if IControlNode.providedBy(source)
        if IActivityNode.providedBy(source):
            self.source = source
        if IActivityNode.providedBy(target):
            self.target = target
        self.guard = guard
        super(ActivityEdge, self).__init__(name)

    @property
    def activity(self):
        return self.__parent__

    def get_source(self):
        return self.node(self.source_uuid)
    def set_source(self, source):
        # TODO: invalidate cache key for target's outgoingEdges method
        self.source_uuid = source.uuid
    source = property(get_source, set_source)

    def get_target(self):
        return self.node(self.target_uuid)
    def set_target(self, target):
        # TODO: invalidate cache key for target's incomingEdges method
        self.target_uuid = target.uuid
    target = property(get_target, set_target)


### Initial and final
class InitialNode(ControlNode):
    implements(IInitialNode)
    abstract = False

    def check_model_constraints(self):
        super(InitialNode, self).check_model_constraints()
        # [1]
        try:
            assert super(InitialNode, self).incoming_edges == []
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  u"InitialNode cannot have incoming edges"

class ActivityFinalNode(FinalNode):
    implements(IActivityFinalNode)
    abstract = False

class FlowFinalNode(FinalNode):
    implements(IFlowFinalNode)
    abstract = False

### More control nodes
class DecisionNode(ControlNode):
    implements(IDecisionNode)
    abstract = False

    def check_model_constraints(self):
        super(DecisionNode, self).check_model_constraints()
        # [1]
        try:
            assert len(self.incoming_edges) is 1
            assert len(self.outgoing_edges) >= 1
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "A DecisionNode has one incoming edge and at least"\
                  "one outgoing edge."


class ForkNode(ControlNode):
    implements(IForkNode)
    abstract = False

    def check_model_constraints(self):
        super(ForkNode, self).check_model_constraints()
        # [1]
        try:
            assert len(self.incoming_edges) is 1
            assert len(self.outgoing_edges) >= 1
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  "A ForkNode has one incoming edge and at least "\
                  "one outgoing edge."


class JoinNode(ControlNode):
    implements(IJoinNode)
    abstract = False

    def check_model_constraints(self):
        super(JoinNode, self).check_model_constraints()
        # [1]
        try:
            assert len(self.incoming_edges) >= 1
            assert len(self.outgoing_edges) is 1
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  u"A join node has one outgoing edge and at least "\
                  u"one incoming edge."


# TODO: UML2's MergeNode behavior does not reduce concurrency
# here the concurrency is reduced if 2 tokens come into the node
# at a time. THIS SHOULD BE CHANGED...
class MergeNode(ControlNode):
    implements(IMergeNode)
    abstract = False

    def check_model_constraints(self):
        super(MergeNode, self).check_model_constraints()
        # [1]
        try:
            assert len(self.incoming_edges) >= 1
            assert len(self.outgoing_edges) is 1
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  u"A merge node has one outgoing edge and at least"\
                  u"one incoming edge."


### Constraints
class Constraint(Element):
    implements(IConstraint)
    abstract = False

    def __init__(self, name=None, specification=None):
        self.specification = specification
        super(Constraint, self).__init__(name)

    @property
    def constrained_element(self):
        return self.__parent__

class PreConstraint(Constraint):
    implements(IPreConstraint)
    abstract = False

class PostConstraint(Constraint):
    implements(IPostConstraint)
    abstract = False

### Profile UML Extension Mechanism
class Profile(Node):
    implements(IProfile)
    abstract = False

    ### TODO: let owned_stereotypes return the stereotypes defined in profile
    #def __init__(self, name):
    #    super(Profile,self).__init__(name)
    #    owned_stereotypes = dict()

    #def add_stereotype(self, name, extentended):
    #    owned_stereotypes['name'] = type(name,
    #                                     (Stereotype,),
    #                                     {'extended': extended})

    # TODO: Add check_model_constraints - profile only part of package

    # TODO: Let Profile be a Package (without attribute "activities") and let
    # profiles applied to profile to distinguish between execution-loading
    # profiles and profiles other ones.

class Stereotype(Node):
    implements(IStereotype)
    abstract = False

    def __init__(self, name=None, profile=None):
        super(Stereotype, self).__init__(name)
        try:
            assert(IProfile.providedBy(profile))
        except AssertionError:
            raise ModelIllFormedException,\
                  str(self) +  " " +\
                  u"Stereotype must have a reference to its Profile"
        self.profile = profile

    @property
    def taggedvalues(self):
        return [o for o in self.filtereditems(ITaggedValue)]

class TaggedValue(Node):
    implements(ITaggedValue)
    abstract = False

    def __init__(self, name=None, value=None):
        self.value = value
        super(TaggedValue, self).__init__(name)


def validate(node):
    """Recursive model validation
    """
    if IElement.providedBy(node):
        node.check_model_constraints()
    for sub in node.filtereditems(IElement):
        validate(sub)

def get_element_by_xmiid(node, xmiid):
    if node.xmiid == xmiid:
        return node
    # TODO: may not get all elements if an INode but not IElement providing
    # element sits within the hierachy
    for el in node.filtereditems(IElement):
        ele = get_element_by_xmiid(el, xmiid)
        if ele is not None:
            return ele
    return None
