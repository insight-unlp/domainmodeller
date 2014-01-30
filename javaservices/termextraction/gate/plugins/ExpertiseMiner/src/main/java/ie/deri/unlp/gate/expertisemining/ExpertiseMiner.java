/*
 *  ExpertiseMiner.java
 *
 *
 * Copyright (c) 2000-2001, The University of Sheffield.
 *
 * This file is part of GATE (see http://gate.ac.uk/), and is free
 * software, licenced under the GNU Library General Public License,
 * Version 2, June1991.
 *
 * A copy of this licence is included in the distribution in the file
 * licence.html, and is also available at http://gate.ac.uk/gate/licence.html.
 *
 *  alesch, 2/2/2009
 *
 *  $Id: ExpertiseMiner.jav 9992 2008-10-31 16:53:29Z ian_roberts $
 *
 * For details on the configuration options, see the user guide:
 * http://gate.ac.uk/cgi-bin/userguide/sec:creole-model:config
 */

package ie.deri.unlp.gate.expertisemining;

import gate.ProcessingResource;
import gate.creole.AbstractProcessingResource;
import gate.creole.metadata.CreoleResource;


/** 
 * This class is the implementation of the resource EXPERTISEMINER.
 */
@CreoleResource(name = "ExpertiseMiner",
        comment = "Add a descriptive comment about this resource")
public class ExpertiseMiner  extends AbstractProcessingResource
  implements ProcessingResource {


} // class ExpertiseMiner
