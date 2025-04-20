## Load packages
library(sf)
library(terra)
library(dplyr)

## Import tree polygon
tree_poly <- st_read("shapefiles/Canop_polygon_m_j_palmier.shp") %>% 
  dplyr::select(Species) %>% 
  dplyr::mutate(Species = case_when(is.na(Species) ~ 5, TRUE ~ Species))


## Import tree location data, where we have tree name
tree_point_names <- sf::st_read("shapefiles/SpeciesName_points.shp")
species_id <- unique(tree_point_names$Species)
# Recreate other id for tree, from 0 to number of tree species
#Tree point                     # Initiate tree id to -1
tp_name_select <- data.frame(); id <- -1
for (tid in species_id) {
  tp_name <- tree_point_names %>% 
    filter(Species == tid) %>% 
    slice(1)
  id <- id + 1
  new_df <- data.frame(id = id, 
                       Species = tid, 
                       Species_name = tp_name$Species_na)
  tp_name_select <- rbind(tp_name_select, new_df)
}

# Add Palm tree info to tp_name_select
tp_name_select <- tp_name_select %>% 
  rbind(data.frame(id = max(tp_name_select$id)+1, Species = 5, 
                   Species_name = "Elaeis_guineensis"))

# Join tree polygon data to tree names
canopy_data <- left_join(x = tree_poly, 
                       y = tp_name_select, 
                       by = "Species") %>% 
  dplyr::select(-Species) %>% 
  dplyr::rename(Species = id)

# Save to disk
sf::st_delete("shapefiles/species_canopy.shp")
sf::st_write(canopy_data, "shapefiles/species_canopy.shp")

# Set id: Class name for yolo
class_names <- unique(paste0(canopy_data$Species, ": ", canopy_data$Species_name))
writeLines(text = class_names, con = "class_names.txt")

# Make grid to crop image into suitable tiles for model training
canopy_grid <- sf::st_make_grid(x = canopy_data, n = 55) %>% 
  sf::st_as_sf() %>% 
  mutate(grid_id = paste0("grid_", 1:nrow(.)))

## Import area of interest shape to clip canopy_grid
aoi <- sf::st_read("shapefiles/area_of_interest.shp") %>% 
  sf::st_transform(crs = st_crs(canopy_grid))
## Clip grid with aoi
canopy_grid <- st_intersection(canopy_grid, aoi) %>% 
  sf::st_as_sf()
plot(canopy_grid[, 1])

# Select only grid with canopy presence (canopy_data)
right_grid <- list()
for(i in 1:nrow(canopy_grid)){
  sing_grid <- canopy_grid[i, ]
  corresp_canopy <- sing_grid %>% 
    sf::st_intersects(y = canopy_data)
  canopy_per_grid <- corresp_canopy %>% unlist() %>% length()
  if(canopy_per_grid){
    right_grid[[i]] <- sing_grid
  }
}
right_grid <- right_grid %>% dplyr::bind_rows()

# Export grid
st_delete("shapefiles/grid_with_tree.shp")
st_write(right_grid, "shapefiles/grid_with_tree.shp")

## Crop image with right_grid
wv_img <- terra::rast("Pansharpen.Band.tiff")
progess_id  <- 0; total <- length(right_grid$grid_id)

# Create directory to save images
out_dir <- "./cropped"; mask_out <- "./mask"
suppressWarnings({dir.create(out_dir); dir.create(mask_out)})

for (name in right_grid$grid_id) {
  # Display a message
  progess_id <- progess_id + 1
  message(paste0("On ", progess_id, "/", total))
  
  sing_grid <- right_grid %>% 
    dplyr::filter(grid_id == name)
  
  # Crop image
  cropped <- terra::crop(x = wv_img, y = sing_grid)
  # Clip canopy tree and make mask
  rasterized <- canopy_data %>% 
    st_make_valid() %>% 
    dplyr::filter(st_is_valid(.)) %>% 
    st_intersection(y = sing_grid) %>% 
    terra::rasterize(x = ., y = cropped, field = "Species", background = 9999)

  ## Write cropped image
  terra::writeRaster(cropped, filename = paste0(out_dir, "/", name, ".tif"),
                    overwrite = TRUE)
  ## Write mask
  terra::writeRaster(rasterized, filename = paste0(mask_out, "/", name, ".tif"),
                    overwrite = TRUE)
}
