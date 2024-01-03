import Head from "next/head"
import Image from "next/image"
import Link from "next/link"

import { useRouter } from "next/router"
import { useState, useEffect } from "react"

import { Nav } from "react-bootstrap"
import { Button } from "react-bootstrap"
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownButton from 'react-bootstrap/DropdownButton'

import WorkspaceHeader from "./_workspaceHeader"

import service from "../service"

import workspaceLayoutStyles from "../styles/WorkspaceLayout.module.css"

export default function WorkspaceLayout({ children }) {
  const router = useRouter();

  let { parserId } = router.query;

  const [parser, setParser] = useState(null)
  const [userProfile, setUserProfile] = useState(null)

  const getParser = () => {
    if (!parserId) return
    service.get("parsers/" + parserId + "/", (response) => {
      setParser(response.data)
    })
  }

  const getUserProfile = () => {
    service.get("profiles/", (response) => {
      setUserProfile(response.data[0])
    })
  }

  const logoutBtnClickHandler = () => {
    service.post("rest-auth/logout/", {}, () => {
      localStorage.removeItem("token")
      router.push("/")
    })
  }

  useEffect(() => {
    getUserProfile()
  }, [])

  useEffect(() => {
    getParser()
  }, [parserId])

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        ></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={workspaceLayoutStyles.wrapper}>
        <WorkspaceHeader />
        <hr className={workspaceLayoutStyles.headerHr} />
        <main className={workspaceLayoutStyles.main + " d-flex flex-column"}>
          <div
            className={
              workspaceLayoutStyles.sideNavContainerDiv + " d-flex flex-grow-1"
            }
          >
            <div
              className="row d-flex flex-grow-1"
              style={{ padding: 0, margin: 0, flexDirection: "row" }}
            >
              <div
                className="col-12 col-md-2 d-flex"
                style={{ paddingLeft: 0, paddingRight: 0, width: 200 }}
              >
                <div
                  className={
                    workspaceLayoutStyles.sideNavDiv + " d-flex flex-grow-1"
                  }
                >
                  <ul className={workspaceLayoutStyles.sideNavUl}>
                    {parser && (
                      <li style={{ fontFamily: "Oswald, sans", fontSize: "130%" }}>{parser.name}</li>
                    )}
                    <Link href={"/workspace/parsers/" + parserId + "/sources"}>
                      <li>Sources</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/queues"}>
                      <li>Queues</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/preprocessings"}>
                      <li>Pre-Processings</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/ocr"}>
                      <li>OCR</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/aichat"}>
                      <li>AI Chat</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/splitting"}>
                      <li>Splitting</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/rules"}>
                      <li>Fields</li>
                    </Link>
                    <Link
                      href={"/workspace/parsers/" + parserId + "/postprocessings"}
                    >
                      <li>Post-Processing</li>
                    </Link>
                    <Link
                      href={"/workspace/parsers/" + parserId + "/integrations"}
                    >
                      <li>Integrations</li>
                    </Link>
                    <Link href={"/workspace/parsers/" + parserId + "/settings"}>
                      <li>Settings</li>
                    </Link>
                  </ul>
                </div>
              </div>
              <div
                className="col-12 col-md-10 flex-grow-1"
                style={{
                  paddingLeft: 0,
                  paddingRight: 0,
                  paddingBottom: 10,
                  minHeight: "480px",
                  display: "flex",
                  width: "calc(100% - 200px)",
                }}
              >
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={workspaceLayoutStyles.footer}>
          <div style={{ width: "100%", padding: "0 10px" }}>
            <div className="row" style={{ padding: "0 10px" }}>
              <div className="col-sm" style={{ padding: "10px" }}>
                <div className={workspaceLayoutStyles.copyright}>
                  2023. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
