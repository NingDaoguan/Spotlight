// povray spotlight.pov +w800 +h800 +a0.1 +am2

#include "colors.inc"     
#include "stones.inc"

global_settings { assumed_gamma 1.5 }

// The camera.

camera {
  location <4, 6, -12>
  look_at <0, 4, 0>
}
  
media {  
  //emission rgb<0,.001,0> 
  //absorption rgb<0,0,0.1>
  scattering { 
       4,  // Rayleigh scattering
       rgb 0.03 
  }  
}    
  
// Center light source not interacting with the atmosphere. 
//light_source { <0, 15, 0> color rgb 1
//  media_interaction off   
//  shadowless 
//}

 
// two Spotlights  

light_source { 
  <-10, 15, -5> 
  color rgb<.5, .5, .3> * 10  spotlight
  point_at <0, 2, 0>   
  
  // These control the way that light tapers off at the edges of the cone
  radius 10      // default 30
  falloff 15     // default  45
  tightness 1    // default 0    
  
  media_attenuation on
}

light_source { 
  <10, 15, 5> 
  color rgb<0.7, .5, .5> * 10  spotlight
//  color rgb<0.1, .3, .9> * 10  spotlight
  point_at <0, 2, 0>   
  
  // These control the way that light tapers off at the edges of the cone
  radius 5      // default 30
  falloff 15     // default  45
  tightness 1    // default 0    
  
  media_attenuation on
}
  
// Room ambient
//sphere { <-0, 0, -0>, 20
//  pigment { rgb 1.5 }
//  finish { ambient 0.2 diffuse 0.5 }
//  hollow
//}  

// An infinite planar surface
// plane {<A, B, C>, D } where: A*x + B*y + C*z = D

plane {
  y,    // <X Y Z> unit surface normal, vector points "away from surface"
  1.0   // distance from the origin in the direction of the surface normal
        // has an inside pigment?
  pigment { rgb <0, .4, .7> }
  finish { ambient 0.1 diffuse 0.5 }
  hollow
}
      
box {
   < 0,  0, 0  >, // Near lower left corner
   < 6,  4, 0.3>  // Far upper right corner
   texture {          
      pigment { image_map {jpeg "spotlight-mac.jpg"}}  
      finish { ambient 0.9 diffuse 0.05 }
      scale <6, 4, 1>
   }  
   rotate <45,20,0>
   translate <-4, 2, 0>
}
