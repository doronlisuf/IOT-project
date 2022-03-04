
class Globals: 
    allServices = {}
    allThings = {}
    allUnbounded = {}
    allUnboundedRelationships = {}
    allRelationships = {}
    allApps = {}
    recipeTable = None # For use in activating apps
    selectedAppRow = 0 
    selectedAppColumn = 0
    parser = None # global parser 
    guiInstance = None # Access gui (for signals) from anywhere
    callsInstance = None
    callThread = None
    servicesTable = None # Used in create recipe tab
    relationshipsTable = None
    
    selectedServiceRow = None # Start off as none if no row has been selected
    selectedServiceColumn = None
    selectedRelRow = None
    selectedRelColumn = None 

    runThread = True

    selectedServicesList = []
    selectedRelationshipsList = []

