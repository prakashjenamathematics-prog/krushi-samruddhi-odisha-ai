import { useEffect, useMemo, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  LayersControl,
  GeoJSON,
} from "react-leaflet";

import L from "leaflet";
import axios from "axios";

import "leaflet/dist/leaflet.css";
import "./App.css";


// ============================================================
// BACKEND API
// ============================================================

const API_BASE_URL = "http://127.0.0.1:5000/api";


// ============================================================
// FIX DEFAULT LEAFLET MARKER ICON
// ============================================================

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});


// ============================================================
// MAP CONTROLLER
// ============================================================

function MapController({
  village,
  villageGeometry,
}) {
  const map = useMap();

  useEffect(() => {

    // --------------------------------------------------------
    // If actual village geometry is available,
    // zoom to the complete village boundary.
    // --------------------------------------------------------

    if (villageGeometry) {

      try {

        const geoJsonLayer = L.geoJSON(
          villageGeometry
        );

        const bounds =
          geoJsonLayer.getBounds();

        if (bounds.isValid()) {

          map.fitBounds(
            bounds,
            {
              padding: [30, 30],
              maxZoom: 16,
              animate: true,
              duration: 1.2,
            }
          );

          return;
        }

      } catch (error) {

        console.error(
          "Failed to fit village boundary:",
          error
        );

      }

    }


    // --------------------------------------------------------
    // Fallback to village coordinates.
    // --------------------------------------------------------

    if (
      village &&
      village.latitude !== null &&
      village.latitude !== undefined &&
      village.longitude !== null &&
      village.longitude !== undefined
    ) {

      const latitude =
        Number(village.latitude);

      const longitude =
        Number(village.longitude);

      if (
        Number.isFinite(latitude) &&
        Number.isFinite(longitude)
      ) {

        map.flyTo(
          [
            latitude,
            longitude
          ],
          14,
          {
            duration: 1.2,
          }
        );

      }

    }

  }, [
    village,
    villageGeometry,
    map
  ]);

  return null;
}


// ============================================================
// APPLICATION
// ============================================================

function App() {

  // ==========================================================
  // LOCATION DATA
  // ==========================================================

  const [districts, setDistricts] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [gps, setGps] = useState([]);
  const [villages, setVillages] = useState([]);


  // ==========================================================
  // SELECTED LOCATION
  // ==========================================================

  const [selectedDistrict, setSelectedDistrict] =
    useState("");

  const [selectedBlock, setSelectedBlock] =
    useState("");

  const [selectedGP, setSelectedGP] =
    useState("");

  const [selectedVillage, setSelectedVillage] =
    useState(null);


  // ==========================================================
  // GIS VILLAGE BOUNDARY
  // ==========================================================

  const [villageGeometry, setVillageGeometry] =
    useState(null);

  const [loadingBoundary, setLoadingBoundary] =
    useState(false);


  // ==========================================================
  // SEARCH
  // ==========================================================

  const [searchText, setSearchText] =
    useState("");


  // ==========================================================
  // LOADING STATES
  // ==========================================================

  const [loadingDistricts, setLoadingDistricts] =
    useState(false);

  const [loadingBlocks, setLoadingBlocks] =
    useState(false);

  const [loadingGPs, setLoadingGPs] =
    useState(false);

  const [loadingVillages, setLoadingVillages] =
    useState(false);


  // ==========================================================
  // ERROR
  // ==========================================================

  const [error, setError] =
    useState("");


  // ==========================================================
  // BACKEND STATUS
  // ==========================================================

  const [backendConnected, setBackendConnected] =
    useState(false);

  const [checkingBackend, setCheckingBackend] =
    useState(true);


  // ==========================================================
  // BACKEND HEALTH CHECK
  // ==========================================================

  useEffect(() => {

    async function checkBackend() {

      try {

        setCheckingBackend(true);

        const response = await axios.get(
          `${API_BASE_URL}/health`,
          {
            timeout: 5000,
          }
        );

        if (
          response.data &&
          response.data.status === "healthy"
        ) {

          setBackendConnected(true);

        } else {

          setBackendConnected(false);

        }

      } catch (err) {

        console.error(
          "Backend health check failed:",
          err
        );

        setBackendConnected(false);

      } finally {

        setCheckingBackend(false);

      }

    }

    checkBackend();

  }, []);


  // ==========================================================
  // LOAD DISTRICTS
  // ==========================================================

  useEffect(() => {

    async function loadDistricts() {

      try {

        setLoadingDistricts(true);
        setError("");

        const response = await axios.get(
          `${API_BASE_URL}/districts`,
          {
            timeout: 10000,
          }
        );

        if (
          response.data &&
          response.data.status === "success"
        ) {

          setDistricts(
            response.data.data || []
          );

          setBackendConnected(true);

        } else {

          setError(
            "Unable to load districts."
          );

        }

      } catch (err) {

        console.error(
          "District loading error:",
          err
        );

        setBackendConnected(false);

        setError(
          "Unable to connect to the Krushi Samruddhi backend."
        );

      } finally {

        setLoadingDistricts(false);

      }

    }

    loadDistricts();

  }, []);


  // ==========================================================
  // DISTRICT CHANGE
  // ==========================================================

  async function handleDistrictChange(event) {

    const districtId =
      event.target.value;

    setSelectedDistrict(
      districtId
    );

    setSelectedBlock("");
    setSelectedGP("");
    setSelectedVillage(null);

    setBlocks([]);
    setGps([]);
    setVillages([]);

    setVillageGeometry(null);

    setSearchText("");
    setError("");


    if (!districtId) {
      return;
    }


    try {

      setLoadingBlocks(true);

      const response = await axios.get(
        `${API_BASE_URL}/blocks/district/${districtId}`,
        {
          timeout: 10000,
        }
      );

      if (
        response.data &&
        response.data.status === "success"
      ) {

        setBlocks(
          response.data.data || []
        );

        setBackendConnected(true);

      } else {

        setError(
          "Unable to load blocks."
        );

      }

    } catch (err) {

      console.error(
        "Block loading error:",
        err
      );

      setBackendConnected(false);

      setError(
        "Unable to load blocks."
      );

    } finally {

      setLoadingBlocks(false);

    }

  }


  // ==========================================================
  // BLOCK CHANGE
  // ==========================================================

  async function handleBlockChange(event) {

    const blockId =
      event.target.value;

    setSelectedBlock(
      blockId
    );

    setSelectedGP("");
    setSelectedVillage(null);

    setGps([]);
    setVillages([]);

    setVillageGeometry(null);

    setSearchText("");
    setError("");


    if (!blockId) {
      return;
    }


    try {

      setLoadingGPs(true);

      const response = await axios.get(
        `${API_BASE_URL}/gps/block/${blockId}`,
        {
          timeout: 10000,
        }
      );

      if (
        response.data &&
        response.data.status === "success"
      ) {

        setGps(
          response.data.data || []
        );

        setBackendConnected(true);

      } else {

        setError(
          "Unable to load Gram Panchayats."
        );

      }

    } catch (err) {

      console.error(
        "GP loading error:",
        err
      );

      setBackendConnected(false);

      setError(
        "Unable to load Gram Panchayats."
      );

    } finally {

      setLoadingGPs(false);

    }

  }


  // ==========================================================
  // GP CHANGE
  // ==========================================================

  async function handleGPChange(event) {

    const gpId =
      event.target.value;

    setSelectedGP(
      gpId
    );

    setSelectedVillage(null);

    setVillages([]);

    setVillageGeometry(null);

    setSearchText("");
    setError("");


    if (!gpId) {
      return;
    }


    try {

      setLoadingVillages(true);

      const response = await axios.get(
        `${API_BASE_URL}/villages/gp/${gpId}`,
        {
          timeout: 10000,
        }
      );

      if (
        response.data &&
        response.data.status === "success"
      ) {

        setVillages(
          response.data.data || []
        );

        setBackendConnected(true);

      } else {

        setError(
          "Unable to load villages."
        );

      }

    } catch (err) {

      console.error(
        "Village loading error:",
        err
      );

      setBackendConnected(false);

      setError(
        "Unable to load villages."
      );

    } finally {

      setLoadingVillages(false);

    }

  }


  // ==========================================================
  // VILLAGE SEARCH
  // ==========================================================

  const filteredVillages =
    useMemo(() => {

      const search =
        searchText
          .trim()
          .toLowerCase();

      if (!search) {

        return villages;

      }


      return villages.filter(
        (village) => {

          const englishName =
            village.village_name_en ||
            "";

          const odiaName =
            village.village_name_or ||
            "";

          const lgdCode =
            village.lgd_code !== null &&
            village.lgd_code !== undefined
              ? String(
                  village.lgd_code
                )
              : "";


          return (
            englishName
              .toLowerCase()
              .includes(search) ||

            odiaName
              .toLowerCase()
              .includes(search) ||

            lgdCode.includes(search)
          );

        }
      );

    }, [
      villages,
      searchText
    ]);


  // ==========================================================
  // SELECT VILLAGE
  // ==========================================================

  async function handleVillageSelect(
    village
  ) {

    setSelectedVillage(
      village
    );

    setVillageGeometry(null);
    setError("");


    if (
      village.lgd_code === null ||
      village.lgd_code === undefined ||
      village.lgd_code === ""
    ) {

      setError(
        "GIS boundary is unavailable because this village does not have an LGD code."
      );

      return;
    }


    try {

      setLoadingBoundary(true);

      const response = await axios.get(
        `${API_BASE_URL}/gis/village/${village.lgd_code}`,
        {
          timeout: 30000,
        }
      );


      if (
        response.data &&
        response.data.status ===
          "success" &&
        response.data.data &&
        response.data.data.geometry
      ) {

        setVillageGeometry(
          response.data.data.geometry
        );

        setBackendConnected(true);

      } else {

        setError(
          "GIS boundary is not available for this village."
        );

      }

    } catch (err) {

      console.error(
        "Village GIS boundary loading error:",
        err
      );

      setError(
        "Unable to load the village GIS boundary."
      );

    } finally {

      setLoadingBoundary(false);

    }

  }


  // ==========================================================
  // STATISTICS
  // ==========================================================

  const totalVillages =
    villages.length;

  const filteredCount =
    filteredVillages.length;

  const totalGPS =
    gps.length;


  // ==========================================================
  // CURRENT ADMINISTRATIVE LEVEL
  // ==========================================================

  const administrativeLevel =
    selectedVillage
      ? "Village"
      : selectedGP
        ? "GP"
        : selectedBlock
          ? "Block"
          : selectedDistrict
            ? "District"
            : "Odisha";


  // ==========================================================
  // VILLAGE BOUNDARY STYLE
  // ==========================================================

  const villageBoundaryStyle = {

    color: "#d62828",

    weight: 4,

    opacity: 1,

    fillColor: "#ef4444",

    fillOpacity: 0.12,

    dashArray: "8 6",

  };


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div className="app">


      {/* =====================================================
    GOVERNMENT HEADER
    ===================================================== */}

<header className="government-header">

  <div className="header-container">

    <div className="government-brand">

      {/* ODISHA GOVERNMENT LOGO */}
      <div className="government-logo">

        <img
          src="/odisha-govt-logo-white.png"
          alt="Government of Odisha"
        />

      </div>


      {/* VERTICAL DIVIDER */}
      <div className="government-divider"></div>


      {/* BRAND TEXT */}
      <div className="brand-text">

        <div className="government-title">
          GOVERNMENT OF ODISHA
        </div>

        <h1>
          Krushi Samruddhi Odisha AI
        </h1>

        <p>
          AI-Powered Village-Level Climate Resilience
          and Agricultural Risk Management Dashboard
        </p>

      </div>

    </div>

  </div>

</header>
      {/* =====================================================
          TOP NAVIGATION
          ===================================================== */}

      <nav className="top-navigation">

        <div className="navigation-container">

          <span className="nav-active">
            Dashboard
          </span>

          <span>
            Village Information
          </span>

          <span>
            Climate Risk
          </span>

          <span>
            Agricultural Intelligence
          </span>

          <span>
            About System
          </span>

        </div>

      </nav>


      {/* =====================================================
          MAIN
          ===================================================== */}

      <main className="main-container">


        {/* ===================================================
            PAGE INTRODUCTION
            =================================================== */}

        <section className="page-introduction">

          <div>

            <div className="breadcrumb">
              Odisha / Agriculture / Village Dashboard
            </div>

            <h2>
              Village-Level Agricultural Intelligence
            </h2>

            <p>
              Select an administrative location to explore
              village information and GIS-based agricultural
              decision support data.
            </p>

          </div>


          <div
            className={`system-status ${
              backendConnected
                ? "system-online"
                : "system-offline"
            }`}
          >

            <span className="status-dot"></span>

            {checkingBackend
              ? "Checking Backend..."
              : backendConnected
                ? "Backend Connected"
                : "Backend Offline"}

          </div>

        </section>


        {/* ===================================================
            ERROR MESSAGE
            =================================================== */}

        {error && (

          <div className="error-message">

            <strong>
              System Notice:
            </strong>

            <span>
              {error}
            </span>

          </div>

        )}


        {/* ===================================================
            ADMINISTRATIVE LOCATION
            =================================================== */}

        <section className="control-panel">

          <div className="section-heading">

            <div>

              <span className="section-number">
                01
              </span>

              <div>

                <h3>
                  Administrative Location
                </h3>

                <p>
                  Select District → Block → Gram Panchayat
                  to load village information.
                </p>

              </div>

            </div>

          </div>


          <div className="selector-grid">


            {/* DISTRICT */}

            <div className="selector-field">

              <label>
                District
              </label>

              <select
                value={selectedDistrict}
                onChange={
                  handleDistrictChange
                }
                disabled={
                  loadingDistricts
                }
              >

                <option value="">

                  {loadingDistricts
                    ? "Loading districts..."
                    : "Select District"}

                </option>


                {districts.map(
                  (district) => (

                    <option
                      key={
                        district.district_id
                      }
                      value={
                        district.district_id
                      }
                    >

                      {
                        district
                          .district_name_en
                      }

                      {" — "}

                      {
                        district
                          .district_name_or
                      }

                    </option>

                  )
                )}

              </select>

            </div>


            {/* BLOCK */}

            <div className="selector-field">

              <label>
                Block
              </label>

              <select
                value={selectedBlock}
                onChange={
                  handleBlockChange
                }
                disabled={
                  !selectedDistrict ||
                  loadingBlocks
                }
              >

                <option value="">

                  {loadingBlocks
                    ? "Loading blocks..."
                    : "Select Block"}

                </option>


                {blocks.map(
                  (block) => (

                    <option
                      key={
                        block.block_id
                      }
                      value={
                        block.block_id
                      }
                    >

                      {
                        block
                          .block_name_en
                      }

                      {block.block_name_or &&
                      block.block_name_or !==
                        block.block_name_en
                        ? ` — ${block.block_name_or}`
                        : ""}

                    </option>

                  )
                )}

              </select>

            </div>


            {/* GP */}

            <div className="selector-field">

              <label>
                Gram Panchayat
              </label>

              <select
                value={selectedGP}
                onChange={
                  handleGPChange
                }
                disabled={
                  !selectedBlock ||
                  loadingGPs
                }
              >

                <option value="">

                  {loadingGPs
                    ? "Loading Gram Panchayats..."
                    : "Select Gram Panchayat"}

                </option>


                {gps.map(
                  (gp) => (

                    <option
                      key={
                        gp.gp_id
                      }
                      value={
                        gp.gp_id
                      }
                    >

                      {
                        gp.gp_name_en
                      }

                      {gp.gp_name_or &&
                      gp.gp_name_or !==
                        gp.gp_name_en
                        ? ` — ${gp.gp_name_or}`
                        : ""}

                    </option>

                  )
                )}

              </select>

            </div>

          </div>

        </section>


        {/* ===================================================
            STATISTICS
            =================================================== */}

        <section className="statistics-grid">


          <div className="stat-card">

            <div className="stat-icon">
              ◉
            </div>

            <div>

              <span>
                Villages Loaded
              </span>

              <strong>
                {totalVillages}
              </strong>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              ◎
            </div>

            <div>

              <span>
                Filtered Villages
              </span>

              <strong>
                {filteredCount}
              </strong>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              ⌖
            </div>

            <div>

              <span>
                Gram Panchayats
              </span>

              <strong>
                {totalGPS}
              </strong>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              ◇
            </div>

            <div>

              <span>
                Administrative Level
              </span>

              <strong className="small-stat">
                {administrativeLevel}
              </strong>

            </div>

          </div>

        </section>


        {/* ===================================================
            MAP + DIRECTORY
            =================================================== */}

        <section className="dashboard-grid">


          {/* =================================================
              GIS MAP
              ================================================= */}

          <div className="map-panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  GIS VIEW
                </span>

                <h3>
                  Village Location Map
                </h3>

              </div>

            </div>


            <div className="map-wrapper">

              <MapContainer

                center={[
                  20.2961,
                  85.8245
                ]}

                zoom={7}

                scrollWheelZoom={true}

                className="leaflet-map"
              >


                {/* =================================================
                    MAP LAYERS
                    ================================================= */}

                <LayersControl
                  position="topright"
                >


                  {/* STREET MAP */}

                  <LayersControl.BaseLayer
                    checked
                    name="Street Map"
                  >

                    <TileLayer

                      attribution='&copy; OpenStreetMap contributors'

                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

                    />

                  </LayersControl.BaseLayer>


                  {/* SATELLITE */}

                  <LayersControl.BaseLayer
                    name="Satellite"
                  >

                    <TileLayer

                      attribution='Tiles &copy; Esri'

                      url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

                    />

                  </LayersControl.BaseLayer>


                </LayersControl>


                {/* =================================================
                    ACTUAL VILLAGE BOUNDARY
                    ================================================= */}

                {villageGeometry && (

                  <GeoJSON

                    key={
                      selectedVillage?.village_id ||
                      "village-boundary"
                    }

                    data={
                      villageGeometry
                    }

                    style={
                      villageBoundaryStyle
                    }

                  />

                )}


                {/* =================================================
                    VILLAGE MARKER
                    ================================================= */}

                {selectedVillage &&
                  selectedVillage.latitude !==
                    null &&
                  selectedVillage.latitude !==
                    undefined &&
                  selectedVillage.longitude !==
                    null &&
                  selectedVillage.longitude !==
                    undefined && (

                    <Marker
                      position={[
                        Number(
                          selectedVillage.latitude
                        ),
                        Number(
                          selectedVillage.longitude
                        ),
                      ]}
                    >

                      <Popup>

                        <strong>
                          {
                            selectedVillage
                              .village_name_en
                          }
                        </strong>

                        <br />

                        {
                          selectedVillage
                            .village_name_or
                        }

                        <br />
                        <br />

                        LGD Code:{" "}

                        {
                          selectedVillage
                            .lgd_code ||
                          "N/A"
                        }

                        <br />

                        Census Code:{" "}

                        {
                          selectedVillage
                            .census_code ||
                          "N/A"
                        }

                      </Popup>

                    </Marker>

                  )}


                {/* =================================================
                    MAP CONTROLLER
                    ================================================= */}

                <MapController

                  village={
                    selectedVillage
                  }

                  villageGeometry={
                    villageGeometry
                  }

                />

              </MapContainer>


              {/* =================================================
                  BOUNDARY LOADING
                  ================================================= */}

              {loadingBoundary && (

                <div className="map-loading-overlay">

                  <div className="map-loading-card">

                    <div className="loading-spinner"></div>

                    <span>
                      Loading village boundary...
                    </span>

                  </div>

                </div>

              )}


              {/* =================================================
                  MAP OVERLAY
                  ================================================= */}

              {!selectedVillage && (

                <div className="map-overlay">

                  <div>

                    <span className="map-pin">
                      ⌖
                    </span>

                    <p>
                      Select a village from the directory
                      to focus the map.
                    </p>

                  </div>

                </div>

              )}

            </div>

          </div>


          {/* =================================================
              VILLAGE DIRECTORY
              ================================================= */}

          <div className="village-panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  VILLAGE DIRECTORY
                </span>

                <h3>
                  Available Villages
                </h3>

              </div>

              <span className="count-badge">
                {filteredCount}
              </span>

            </div>


            <div className="search-box">

              <input
                type="text"
                placeholder="Search village or LGD code..."
                value={searchText}
                onChange={
                  (event) =>
                    setSearchText(
                      event.target.value
                    )
                }
              />

            </div>


            <div className="village-list">


              {!selectedGP && (

                <div className="empty-state">

                  <div>
                    ◫
                  </div>

                  <p>
                    Select a District, Block and Gram
                    Panchayat to view villages.
                  </p>

                </div>

              )}


              {selectedGP &&
                loadingVillages && (

                  <div className="empty-state">

                    <div className="loading-spinner"></div>

                    <p>
                      Loading village information...
                    </p>

                  </div>

                )}


              {selectedGP &&
                !loadingVillages &&
                filteredVillages.length === 0 && (

                  <div className="empty-state">

                    <div>
                      ⌕
                    </div>

                    <p>
                      No villages found.
                    </p>

                  </div>

                )}


              {filteredVillages.map(
                (village) => (

                  <button
                    type="button"

                    className={`village-item ${
                      selectedVillage?.village_id ===
                      village.village_id
                        ? "selected"
                        : ""
                    }`}

                    key={
                      village.village_id
                    }

                    onClick={() =>
                      handleVillageSelect(
                        village
                      )
                    }
                  >

                    <div className="village-item-main">

                      <strong>
                        {
                          village
                            .village_name_en
                        }
                      </strong>

                      <span>
                        {
                          village
                            .village_name_or
                        }
                      </span>

                    </div>


                    <div className="village-code">

                      LGD

                      <strong>
                        {
                          village.lgd_code ||
                          "N/A"
                        }
                      </strong>

                    </div>

                  </button>
                )
              )}

            </div>

          </div>

        </section>


        {/* ===================================================
            SELECTED VILLAGE DETAILS
            =================================================== */}

        {selectedVillage && (

          <section className="village-details">

            <div className="details-heading">

              <div>

                <span>
                  SELECTED VILLAGE
                </span>

                <h3>
                  {
                    selectedVillage
                      .village_name_en
                  }
                </h3>

              </div>


              <div className="details-code">

                LGD CODE

                <strong>
                  {
                    selectedVillage
                      .lgd_code ||
                    "N/A"
                  }
                </strong>

              </div>

            </div>


            <div className="details-grid">


              <div>

                <span>
                  Village Name (Odia)
                </span>

                <strong>
                  {
                    selectedVillage
                      .village_name_or ||
                    "N/A"
                  }
                </strong>

              </div>


              <div>

                <span>
                  Census Code
                </span>

                <strong>
                  {
                    selectedVillage
                      .census_code ||
                    "N/A"
                  }
                </strong>

              </div>


              <div>

                <span>
                  Latitude
                </span>

                <strong>
                  {
                    selectedVillage
                      .latitude ??
                    "N/A"
                  }
                </strong>

              </div>


              <div>

                <span>
                  Longitude
                </span>

                <strong>
                  {
                    selectedVillage
                      .longitude ??
                    "N/A"
                  }
                </strong>

              </div>

            </div>

          </section>

        )}

      </main>


     {/* =====================================================
    GOVERNMENT FOOTER
    ===================================================== */}

<footer className="government-footer">

  <div className="footer-container">

    <div className="footer-brand">

      {/* FOOTER LOGO */}

      <div className="footer-logo">

        <img
          src="/odisha-govt-logo-white.png"
          alt="Government of Odisha"
        />

      </div>


      {/* FOOTER DIVIDER */}

      <div className="footer-divider"></div>


      {/* FOOTER TEXT */}

      <div className="footer-text">

        <strong>
          Krushi Samruddhi Odisha AI
        </strong>

        <p>
          AI-enabled GIS-based village-level
          agricultural risk management platform.
        </p>

      </div>

    </div>


    {/* GOVERNMENT TEXT */}

    <div className="footer-government">

      <span>
        Government of Odisha
      </span>

    </div>

  </div>

</footer>


    </div>

  );
}


export default App;