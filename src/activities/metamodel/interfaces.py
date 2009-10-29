# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at> and
                Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'


from zope.interface import Interface
from zope.interface import Attribute
from zodict.interfaces import INode

"""Literature:
[1] OMG Unified Modeling LanguageTM (OMG UML), Superstructure. Version 2.2.
[2] The Unified Modeling Language Reference Manual Second Edition.
    James Rumbaugh, Ivar Jacobson, Grady Booch. Addison-Wesley, 2005
"""

"""Elements not covered:
- Class (from Kernel)
- Classifier (from Kernel, Dependencies, PowerTypes)
- Element (from Kernel)
- NamedElement (from Kernel, Dependencies)
- Namespace (from Kernel)
- RedefinableElement (from Kernel)
The important features (name, namespace(=path), containment, inheritance, ...)
are either supported by zodict.node.Node from which our metamodel classes
inherit from or by Python. No further metamodel formalization.

Packages not covered:
- StructuredActivities (including Subpackages)

Activity model elements not covered:
- ActionInputPin
- ActivityGroup
- ActivityParameterNode
- ActivityPartition
- BehavioralFeature
- CentralBufferNode
- Clause
- DataStoreNode
- ExceptionHandler
- ExecutableNode
- ExpansionKind
- ExpansionNode
- ExpansionRegion
- InterruptibleActivityRegion
- LoopNode
- ObjectNodeOrderingKind
- Parameter
- ParameterEffectKind
- ParameterSet
- SequenceNode
- StructuredActivityNode
- Variable

Actions not covered:
- AcceptEventAction
- AddVariableValueAction
- CallBehaviorAction
- CallOperationAction
- SendObjectAction
- SendSignalAction
- UnmarshallAction
- ValueSpecificationAction
"""


### HELPER INTERFACES
class ActivitiesException(Exception):
    """Base class for activities.metamodel exceptions"""

### ABSTRACT BASE CLASSES
class IElement(INode):
    """Base class of all elements.
    """

    def check_model_constraints(self):
        """Since some rules cannot be evaluated at instantiation time this
        function should be called on model elements by the interpreter when
        building the concrete model.

        Don't confuse this with "Constraint" from UML specification

        All "check_model_constraints" methods  through the whole inheritance
        hierarchy should be called. It's up to the implementation to call the
        superclass' "check_model_constraints" implementation.

        For example, consider a model element which must have a parent:
            node['element'] = Element()
        Element does not have a parent at instatiation time.
        """

    # TODO: annotate XMI to Element to seperate this model interchange specific
    # issue from metamodel
    xmiid = Attribute(
        u'id of the corresponding element from xmi model file'
    )

    stereotypes = Attribute(
        u"""The stereotype extension of the element.
        Used to specify concrete actions on the general actions model element.
        """
    )

class IActivityEdge(IElement):
    """Abstract Base Class
    An activity edge is an abstract class for directed connections between two
    activity nodes. ([1], pg. 325)

    A sequencing relationship between two activity nodes, possibly including
    data. ([2], pg. 157)

    Generalizations not covered:
    - RedefinableElement (from Kernel)

    Associations not covered:
    - /inGroup : ActivityGroup[0..*]
    - redefinedEdge: ActivityEdge [0..*]
    - inPartition : Partition [0..*]
    - inStructuredNode : StructuredActivityNode [0..1]
    - interrupts : InterruptibleActivityRegion [0..1]
    - weight : ValueSpecification [1..1] = 1 (weight always 1)

    Associations:
    - source : ActivityNode [1..1]
      source : IActivityNode [1..1]
    - target : ActivityNode [1..1]
      target : IActivityNode [1..1]

    Associations different from specification:
    - activity : Activity[0..1]
      activity : IActivity [1]
    - guard : ValueSpecification [1..1] = true
      #guard : IConstraint[0..1] = true
      guard : String[0..1]

      Constraints not covered:
      Package CompleteStructuredActivities: [1]

      Constraints:
      [1] The source and target of an edge must be in the same activity as the
          edge.

      Constraints different from specification:
      [2] Activity edges must be owned by activities and only by them.
    """
    activity = Attribute(
        u'Activity containing the edge. Computed property'
    )
    source = Attribute(
        u'Node from which tokens are taken when they traverse the edge.'
        u'Provices IActivityNode objects.'
    )
    target = Attribute(
        u'Node to which tokens are put when they traverse the edge.'
        u'Provices IActivityNode objects.'
    )
    guard = Attribute(
        u'Specification evaluated at runtime to determine if the edge can be'
        u'traversed. A python expression which must evaluate to True'
    )


class IActivityNode(IElement):
    """Abstract Base Class
    An activity node is an abstract class for points in the flow of an
    activity connected by edges. ([1], 333)

    A kind of element in an activity that can be connected by flows. This
    is an abstract element type whose specific varieties include actions,
    control nodes, object nodes (including pins and parameter nodes), and
    structured nodes. ([2], 159ff)

    Associations not covered:
    - /inGroup : Group [0..*]
    - redefinedNode : ActivityNode [0..*]
    - inPartition : Partition [0..*]
    - inInterruptibleRegion : InterruptibleActivityRegion [0..*]
    - inStructuredNode : StructuredActivityNode [0..1]

    Associations different from specification:
    - activity : Activity[0..1]
      activity : Activity [1]
    - incoming : ActivityEdge [0..*]
      incoming_edges : IActivityEdge [0..*]
    - outgoing : ActivityEdge [0..*]
      outgoing_edges : IActivityEdge [0..*]

    Constraints different from specification:
    [1] Activity nodes can only be owned by activities.

    """
    activity = Attribute(
        u'Activity the ActivityNode belongs to. Computed property'
    )
    incoming_edges = Attribute(
        u'Edges that have the node as target. Computed property'
    )
    outgoing_edges = Attribute(
        u'Edges that have the node as source. Computed property'
    )


class IAction(IActivityNode):
    """Abstract Base Class
    A primitive activity node whose execution results in a change in the
    state of the system or the return of a value. ([2], pg.136)

    Generalizations not covered:
    - ExecutableNode (from ExtraStructuredActivities, StructuredActivities)
      Exception handler usage not covered yet.

    Associations not covered:
    - /input : InputPin [*]
    - /output : OutputPin [*]

    Associations different from specification:
    - /context : Classifier [0..1]
      context : object [0..1]
    - localPreconditions : Constraint [0..*]
      preconditions : IPreConstraint [0..*]
    - localPostconditions : Constraint [0..*]
      postconditions : IPostConstraint [0..*]
    """
    context = Attribute(
        u'The classifier that owns the behavior of which this action is a part.'
        u'Computed.'
    )
    preconditions = Attribute(
        u'Constraint that must be satisfied when execution is started.'
        u'List of IConstraints.'
    )
    postconditions = Attribute(
        u'Constraint that must be satisfied when execution is completed.'
        u'List of IConstraints.'
    )


class IBehavior(IElement):
    """Abstract Base Class
    Behavior is a specification of how its context classifier changes state
    over time. ([1], 430)

    A specification of how the state of a classifier changes over time. Behavior
    is specialized into activity, interaction, and state machine. A behavior
    describes the dynamics of an entire classifier as a unit. ([2], 190)

    Attributes not covered:
    - isReentrant: Boolean [1]
      Invocation while still executing from previous invocation not allowed.

    Associations not covered:
    - specification: BehavioralFeature [0..1]
      There is always a special invocation of behavior. Passing parameters
      through the calling method is not supported and not needed because the
      behavior has access to any attribute of it's context.
    - ownedParameter: Parameter
      Parameters are available by the context.
    - redefinedBehavior: Behavior

    Associations different from specification:
    - /context: BehavioredClassifier [0..1]
      /context: object[0..1]
    - precondition: Constraint
      preconditions: IPreConstraint
    - postcondition: Constraint
      postconditions: IPostConstraint

    Constraints not covered:
    [1], [2], [3], [4]
    """
    context = Attribute(
        u'The classifier that is the context for the execution of the behavior.'
    )
    preconditions = Attribute(
        u'List of IConstraints which must evaluate to True when the behavior is'
        u'invoked.'
    )
    postconditions = Attribute(
        u'List of IConstraints which must evaluate to True when the behavior is'
        u'completed.'
    )


class IControlNode(IActivityNode):
    """Abstract Base Class
    A control node is an abstract activity node that coordinates flows in an
    activity. ([1], pg.356)
    """


class IFinalNode(IControlNode):
    """Abstract Base Class
    A final node is an abstract control node at which a flow in an activity
    stops. ([1], pg.373)

    Constraints:
    [1] A final node has no outgoing edges.
    """
    outgoing_edges = Attribute(u'Is always empty.')


### CONCRETE CLASSES
class IPackage(IElement):
    """A package is used to group elements, and provides a namespace for the
    grouped elements. ([1], pg. 107)

    Generalizations not covered:
    - Namespace (from Kernel)
    - PackageableElement (from Kernel)

    Assoziations not covered:
    - /nestedPackage
    - /packagedElement
    - /ownedType
    - packageMerge
    - nestingPackage

    Constraints not covered:
    - [1] If an element that is owned by a package has visibility, it is public
    or private.
    """
    profiles = Attribute(u'List of IProfiles which are applied to the package')
    activities = Attribute(u'List of IActivities defined in the package')

class IActivity(IBehavior):
    """An activity is the specification of parameterized behavior as the
    coordinated sequencing of subordinate units whose individual elements are
    actions. ([1], 315)

    A specification of executable behavior as the coordinated sequential and
    concurrent execution of subordinate units, including nested activities and
    ultimately individual actions connected by flows from outputs of one node
    to inputs of another. Activities can be invoked by actions and as
    constituents of other behaviors, such as state machine transitions.
    ([2], 149ff)

    Attributes not covered:
    - isReadOnly : Boolean = false
    - isSingleExecution : Boolean = false

    Associations not covered:
    - group : ActivityGroup [0..*]
    - partition : ActivityPartition [0..*]
    - /structuredNode : StructuredActivityNode [0..*]
    - variable : Variable [0..*]

    Associations different from specification:
    - node : ActivityNode [0..*]
      nodes : IActivityNode [0..*]
    - edge : ActivityEdge [0..*]
      edges : IActivityEdge [0..*]
    - package : IPackage [1]

    Constraints not covered:
    [1] The nodes of the activity must include one ActivityParameterNode for
        each parameter.
    [2] An activity cannot be autonomous and have a classifier or behavioral
        feature context at the same time.
    [3] The groups of an activity have no supergroups.

    Constraints different from specification:
    [4] An activity must have exactly one package as parent.
    """

    nodes = Attribute(
        u'Nodes coordinated by the activity.'
        u'List of IActivityNode providing objects, Owned.'
    )
    edges = Attribute(
        u'Edges expressing flow between nodes of the activity.'
        u'List of IEdge providing objects, Owned.'
    )
    # convinience accessor
    actions = Attribute(
        u'List of IAction providing objects, Owned'
    )

class IOpaqueAction(IAction):
    """An action with implementation-specific semantics. ([1], pg.262)

    A primitive activity node whose execution results in a change in the
    state of the system or the return of a value. ([2], pg.136)

    Attributes:

    Associations not covered.
    - language : String [0..*]
      Always Python.
    - inputValue : InputPin [0..*]
      InputValues can be passed by input_pins.
    - outputValue : OutputPin [0..*]
      OutputValues can be passed by output_pins.
    - body : String [0..*]. Different semantics in activities.metamodel.

    """

### Initial and final
class IInitialNode(IControlNode):
    """An initial node is a control node at which flow starts when the activity
    is invoked. ([1], pg.378)

    [1], pg. 378 does not define the constraint that initial nodes can only have
    one outgoing edge but [2], pg. 392 makes such a definition.


    Constraints:
    [1] An initial node has no incoming edges.

    Constraints not covered:
    [2] Only control edges can have initial nodes as source.
    """
    incoming_edges = Attribute(u'Is always empty.')


class IActivityFinalNode(IFinalNode):
    """An activity final node is a final node that stops all flows in an
    activity. ([1], pg. 330)

    A node in an activity specification whose execution causes the forced
    termination of all flows in the activity and the termination of execution
    of the activity. ([2], pg.158)
    """


class IFlowFinalNode(IFinalNode):
    """A flow final node is a final node that terminates a flow. ([1], pg.375)
    """


### More control nodes
class IDecisionNode(IControlNode):
    """A decision node is a control node that chooses between outgoing flows.
    ([1], pg. 360)

    Associations not covered:
    - decisionInput : Behavior [0..1]
      Decicions are made through guard specifications on edges.
    - decisionInputFlow : ObjectFlow [0..1]
      Input values are only accessed through the activities' context.

    Constraints not covered:
    [3], [4], [5], [6], [7], [8]
    [2] The edges coming into and out of a decision node must be either all
        object flows or all control flows.

    Constraints different from specification:
    [1] A decision node has one incoming edge and at least one outgoing edge.

    Semantics:
        - A decision node has XOR semantics
    """


class IForkNode(IControlNode):
    """A fork node is a control node that splits a flow into multiple concurrent
    flows. ([1], pg. 376)

    Constraints different from specification:
    [1] A fork node has one incoming edge and at least one outgoing edge.

    Constraints not covered:
    [2] The edges coming into and out of a fork node must be either all object
        flows or all control flows.
    """


class IJoinNode(IControlNode):
    """A join node is a control node that synchronizes multiple flows. ([1],
    pg. 381)

    Attributes not covered
    - isCombineDuplicate : Boolean [1..1]
      Tokens with same identity will always be combined.

    Associations not covered
    - joinSpec : ValueSpecification [1..1]
      Default is "and". Use merge node for "or" semantic.


    Constraints different from specification:
    [1] A join node has one outgoing edge and at least one incoming edge.

    Constraints not covered:
    [2] If a join node has an incoming object flow, it must have an outgoing
        object flow, otherwise, it must have an outgoing control flow.
    """


class IMergeNode(IControlNode):
    """A merge node is a control node that brings together multiple alternate
    flows. It is not used to synchronize concurrent flows but to accept one
    among several alternate flows. ([1], pg. 387)

    Constraints different from specification:
    [1] A merge node has one outgoing edge and at least one incoming edge.

    Constraints not covered:
    [2] The edges coming into and out of a merge node must be either all object
        flows or all control flows.
    """


### Constraints
# TODO: decide wether to use IConstraint for guard conditions or not
class IConstraint(IElement):
    """UML: A constraint is a condition or restriction expressed in natural
    language text or in a machine readable language for the purpose of declaring
    some of the semantics of an element. ([1], pg. 58)

    A constraint is a condition or restriction expressed as Python code.
    The constraint's expression must evaluate to Boolean True to fullfill the
    constraint. The context of the constraint is the element which references
    the constraint and for which the rule apply. A constraint has access to all
    Attributes the context provides.

    Generalizations not covered:
    - PackageableElement (from Kernel)

    Associations not covered:
    - / context: Namespace [0..1]
      The context is the element which refers to this constraint.

    Associations different from specification:
    - constrainedElement: Element[*]
      constrained_element: object[1]
    - specification: ValueSpecification[1]
      specification: String[1]

    Constraints
    [1] The value specification for a constraint must evaluate to a Boolean
        value.
    [2] Evaluating the value specification for a constraint must not have side
        effects.

    Constraints not covered:
    [3] A constraint cannot be applied to itself. (IConstraint does not have
        the ability to contain something. It does not derive from Node)
    """
    specification = Attribute(
        u"The python expression which must be fulfilled."
    )
    constrained_element = Attribute(
        u"The element which references the constraint."
        u"This element is the constraint's context."
    )

class IPreConstraint(IConstraint):
    """Marker interface for conditions which must be evaluated before any other
    operations.
    """

class IPostConstraint(IConstraint):
    """Marker interface for conditions which must be evaluated at the end of
    an Activity or after an actions was executed.
    """



### Profile UML Extension Mechanism
class IProfile(INode):
    """UML Profile
    No support for nested profiles. Therefore IProfile does not inherit from
    IPackage.
    """
    stereotypes = Attribute(
        u"""List of IStereotype elements defined in the profile.""")

class IStereotype(INode):
    """UML stereotype
    """
    taggedvalues = Attribute(
        u"""List of ITaggedValue elements defined in stereotype""")

class ITaggedValue(INode):
    """UML tagged value.
    """
    value = Attribute(
        u"""The concrete value of the tagged value element""")
#