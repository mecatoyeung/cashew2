import Head from 'next/head';

import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { Button } from 'react-bootstrap'

import PublicLayout from '../layouts/public'

import homeStyles from "../styles/Home.module.css"

const movingContentList = [
  "Invoices.",
  "Delivery Orders.",
  "Billing Documents.",
  "Receipts."
]

let movingContentBreakdowns = []

for (let i=0; i<movingContentList.length; i++) {
  let currentContent = movingContentList[i]
  for (let j=0; j<currentContent.length; j++) {
    movingContentBreakdowns.push(currentContent.substring(0, j))
  }
  for (let j=0; j<10; j++) {
    movingContentBreakdowns.push(currentContent)
  }
  for (let j=currentContent.length; j>0; j--) {
    movingContentBreakdowns.push(currentContent.substring(0, j))
  }
}

export default function Home() {

  const router = useRouter()

  const [movingContentBreakdownIndex, setMovingContentBreakdownIndex] = useState(0)

  const [expandHamburgerMenu, setExpandHamburgerMenu] = useState(false)

  useEffect(() => {
    const adsMovingContentInterval = setInterval(() => {
      if (movingContentBreakdownIndex < movingContentBreakdowns.length) {
        setMovingContentBreakdownIndex(movingContentBreakdownIndex + 1)
      } else {
        setMovingContentBreakdownIndex(0)
      }
    }, 50);
    return () => clearInterval(adsMovingContentInterval);
  }, [movingContentBreakdownIndex]);

  return (
    <>
      <Head>
        <title>Cashew - Homepage</title>
      </Head>
      <PublicLayout>
        <div className={homeStyles.wrapper}>
          <header className={homeStyles.header}>
            <div className="container">
              <div className="row">
                <div className="col-12 col-lg-4">
                  <div className={homeStyles.logoDiv}>
                    <Image src="/static/img/logo.png" width="80" height="71" alt="Cashew Docparser" />
                  </div>
                  <h1 className={homeStyles.h1}>Cashew</h1>
                </div>
                <div className="col-12 col-lg-8">
                  <div className='hamburger-menu'>
                    <span onClick={() => { setExpandHamburgerMenu(true) }}>
                      <i className="bi bi-list"
                        style={{display: expandHamburgerMenu ? "none": "inline-block" }}></i>
                    </span>
                    <span onClick={() => setExpandHamburgerMenu(false)}>
                      <i className="bi bi-x-lg"
                        style={{display: expandHamburgerMenu ? "inline-block": "none" }}></i>
                    </span>
                  </div>
                  <nav className={homeStyles.hamburgerNav} style={{display: expandHamburgerMenu ? "block": "none" }}>
                    <ul>
                      <li>Why Cashew?</li>
                      <li>Solutions</li>
                      <li>Team</li>
                      <li>About Us</li>
                      <li>Contact Us</li>
                    </ul>
                  </nav>
                  <nav className={homeStyles.nav}>
                    <ul>
                      <li>Why Cashew?</li>
                      <li>Solutions</li>
                      <li>Team</li>
                      <li>About Us</li>
                      <li>Contact Us</li>
                    </ul>
                  </nav>
                </div>
              </div>
            </div>
          </header>
          <hr className={homeStyles.headerHr}/>
          <main className={homeStyles.main}>
            <div className="container">
              <div className="row">
                <div className="col-sm col-lg-8" style={{marginBottom: 10}}>
                  <div className={homeStyles.ad}>
                    <div className={homeStyles.content}>
                      <div className={homeStyles.movingContent}>
                        Our company need Document Automation for <span className={homeStyles.movingWords}>{movingContentBreakdowns[movingContentBreakdownIndex]}</span>
                      </div>
                    </div>
                    <div className={homeStyles.actions}>
                      <Button className={homeStyles.btn + " signupBtn"} style={{marginTop: "10px"}} onClick={() => router.push("/signup")}>Try now!</Button>
                      <Button className={homeStyles.btn + " signinBtn"} style={{marginTop: "10px"}} onClick={() => router.push("/signin")}>Sign in.</Button>
                    </div>
                  </div>
                </div>
                <div className="col-sm col-lg-4" style={{marginBottom: 10}}>
                  <div className={homeStyles.sideAd}>
                    <div className={homeStyles.content}>
                      Not conviced?
                    </div>
                    <div className={homeStyles.talkToOurSales}>
                      <Button className={homeStyles.talkToOurSales}>Arrange for a Demo!</Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
          <footer className={homeStyles.footer}>
            <div className="container">
              <div className="row">
                <div className="col-sm">
                  <div className={homeStyles.copyright}>
                    2023.2 All rights reserved.
                  </div>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </PublicLayout>
    </>
  )
}
