import Head from 'next/head'
import Image from "next/image"

import { Button } from 'react-bootstrap'

import workspaceLayoutStyles from "../styles/WorkspaceLayout.module.scss"

export default function WorkspaceLayout({
    children
  }) {
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
          <div className="container">
            <div className="row">
              <div className="col-sm-4">
                <div className={workspaceLayoutStyles.logoDiv}>
                  <Image src="/img/logo.png" width="40" height="36" alt="Cashew Docparser" />
                </div>
                <h1 className={workspaceLayoutStyles.h1}>Cashew Docparser</h1>
              </div>
              <div className="col-sm-8">
                <nav className={workspaceLayoutStyles.nav}>
                  <ul>
                    <li>Welcome, Cato Yeung!</li>
                    <li>
                      <Button className="btn">Logout</Button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <hr className={workspaceLayoutStyles.headerHr}/>
        <main className={workspaceLayoutStyles.main + " d-flex flex-column"}>
          <div className="container d-flex flex-grow-1">
            <div className="row d-flex flex-grow-1">
              <div className="col-sm-2 d-flex flex-grow-1">
                <div className={workspaceLayoutStyles.sideNavDiv + " d-flex flex-grow-1"}>
                  <ul className={workspaceLayoutStyles.sideNavUl}>
                    <li>Parsers</li>
                    <li>Sources</li>
                    <li>Spliting</li>
                    <li>Layouts</li>
                    <li>Integration</li>
                  </ul>
                </div>
              </div>
              <div className="col-sm-10" style={{paddingLeft: 0}}>
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={workspaceLayoutStyles.footer}>
          <div className="container">
            <div className="row">
              <div className="col-sm col-lg-8">
                <div className={workspaceLayoutStyles.copyright}>
                  2023 @ Sonik Global Limited. All rights reserved.
                </div>
              </div>
              <div className="col-sm col-lg-4">
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