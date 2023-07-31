import Head from 'next/head'
import Image from "next/image"
import Link from 'next/link'

import { useRouter } from 'next/router'

import { Nav } from 'react-bootstrap'
import { Button } from 'react-bootstrap'

import service from '../service'

import workspaceLayoutStyles from "../styles/WorkspaceLayout.module.css"

export default function WorkspaceLayout({
    children
  }) {

  const router = useRouter()

  let { parserId } = router.query

  const logoutBtnClickHandler = () => {
    service.post("rest-auth/logout/", {}
      , () => {
        localStorage.removeItem("token")
      router.push("/")
    })
  }

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={workspaceLayoutStyles.wrapper}>
        <header className={workspaceLayoutStyles.header}>
          <div>
            <div className="row" style={{ padding: 0, margin: 0 }}>
              <div className="col-6 col-md-6" style={{paddingLeft: 20, paddingRight: 0}}>
                <div className={workspaceLayoutStyles.logoDiv}>
                  <Image src="/static/img/logo.png" width="40" height="36" alt="Cashew Docparser" />
                </div>
                <h1 className={workspaceLayoutStyles.h1}>Cashew</h1>
                <Nav.Link href="/parsers" style={{display: "inline-block", verticalAlign: "top"}}>
                  <i className={workspaceLayoutStyles.parsersIcon + " bi bi-grid"}></i>
                </Nav.Link>
              </div>
              <div className="col-6 col-md-6" style={{paddingLeft: 0, paddingRight: 20}}>
                <nav className={workspaceLayoutStyles.nav}>
                  <ul>
                    <li>
                      <Button className="btn" onClick={logoutBtnClickHandler}>Logout</Button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <hr className={workspaceLayoutStyles.headerHr}/>
        <main className={workspaceLayoutStyles.main + " d-flex flex-column"}>
          <div className={workspaceLayoutStyles.sideNavContainerDiv + " d-flex flex-grow-1"}>
            <div className="row d-flex flex-grow-1" style={{ padding: 0, margin: 0, flexDirection: "row" }}>
              <div className="col-12 col-md-2 d-flex" style={{paddingLeft: 0, paddingRight: 0, width: 200}}>
                <div className={workspaceLayoutStyles.sideNavDiv + " d-flex flex-grow-1"}>
                  <ul className={workspaceLayoutStyles.sideNavUl}>
                    <li>Sources</li>
                    <Link href={"/workspace/parsers/" + parserId + "/queues"}>
                      <li>Queues</li>
                    </Link>
                    <li>Spliting</li>
                    <li>Layouts</li>
                    <li>Integration</li>
                  </ul>
                </div>
              </div>
              <div className="col-12 col-md-10 flex-grow-1" style={{paddingLeft: 0, paddingRight: 0, paddingBottom: 10, minHeight: "480px", display: "flex", width: "calc(100% - 200px)"}}>
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={workspaceLayoutStyles.footer}>
          <div style={{width: "100%", padding: "0 10px"}}>
            <div className="row" style={{ padding: "0 10px" }}>
              <div className="col-sm col-lg-8" style={{ padding: "10px" }}>
                <div className={workspaceLayoutStyles.copyright}>
                  2023 @ Sonik Global Limited. All rights reserved.
                </div>
              </div>
              <div className="col-sm col-lg-4" style={{ padding: "10px"}}>
                <div className="social-media">
                  <i className="fa fa-instagram" aria-hidden="true"></i>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}