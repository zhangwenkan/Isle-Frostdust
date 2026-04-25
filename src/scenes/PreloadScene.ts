import * as Phaser from 'phaser';

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super('PreloadScene');
  }

  preload(): void {
    const { width, height } = this.scale;

    this.add.rectangle(width / 2, height / 2, 180, 12, 0x221b33).setOrigin(0.5);

    const progressBar = this.add.rectangle(
      width / 2 - 86,
      height / 2,
      4,
      8,
      0xf0d18c
    ).setOrigin(0, 0.5);

    this.load.on('progress', (value: number) => {
      progressBar.width = 172 * value;
    });
  }

  create(): void {
    this.scene.start('MainScene');
  }
}
